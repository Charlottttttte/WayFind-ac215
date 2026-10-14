#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


DEGREE_REQUIREMENTS_URL = "https://seas.harvard.edu/masters-data-science/degree-requirements"
SEAS_COURSES_URL = "https://seas.harvard.edu/masters-data-science/courses"
SCOPE = "Harvard SEAS/GSAS SM in Data Science relevant courses."

OUTPUT_COLUMNS = [
    "dataset_version",
    "retrieved_at",
    "course_key",
    "course_id",
    "course_id_type",
    "subject_catalog",
    "title",
    "school",
    "department",
    "term",
    "credits",
    "instructors",
    "meeting_days",
    "meeting_time",
    "requirement_area",
    "description",
    "source_urls",
    "missing_or_uncertain_fields",
]


@dataclass
class SourcePage:
    url: str
    cache_path: str
    status: int | None
    error: str | None


@dataclass
class CourseRecord:
    dataset_version: str
    retrieved_at: str
    course_key: str
    course_id: str
    course_id_type: str
    subject_catalog: str
    title: str
    school: str
    department: str
    term: str
    credits: int | str
    instructors: str
    meeting_days: str
    meeting_time: str
    requirement_area: str
    description: str
    source_urls: str
    missing_or_uncertain_fields: str


# Prevents excessive spacing and normalizes scraped data so that scraped sentences have natural spacing.
def normalize_space(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


# Converts HTML into plain text.
def strip_tags(markup: str) -> str:
    markup = re.sub(r"<br\s*/?>", "\n", markup, flags=re.I)
    markup = re.sub(r"</(p|div|li|h\d|tr)>", "\n", markup, flags=re.I)
    return normalize_space(html.unescape(re.sub(r"<[^>]+>", " ", markup)))


# URLs have slashes, question marks, etc, so they are not great filenames, cache_name() converts each URL into a shorter, safer filename.
# HTML downloaded pages are saved locally so that the same page doesn't have to be fetched again in a later run.
def cache_name(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16] + ".html"


# fetch_url downloads a web page and saves a local copy. It creates a folder if a folder doesn't already exist, builds a filename using cache_name(url), checks if the file already exists locally, and if the file does not already exist, it sends an HTTP request to the URL. A SourcePage object is returned (SourcePage is metadata about a saved or attempted page) and read_cached_text reads the downloaded HTML as text.
def fetch_url(url: str, cache_dir: Path, refresh: bool) -> SourcePage:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / cache_name(url)
    if cache_path.exists() and not refresh:
        return SourcePage(url=url, cache_path=str(cache_path), status=200, error=None)

    request = urllib.request.Request(url, headers={"User-Agent": "ac215-course-data-pipeline/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            cache_path.write_bytes(response.read())
            return SourcePage(url=url, cache_path=str(cache_path), status=response.status, error=None)
    except urllib.error.HTTPError as exc:
        return SourcePage(url=url, cache_path=str(cache_path), status=exc.code, error=repr(exc))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return SourcePage(url=url, cache_path=str(cache_path), status=None, error=repr(exc))


def read_cached_text(source: SourcePage) -> str:
    path = Path(source.cache_path)
    if not path.exists():
        return ""
    return path.read_text(errors="ignore")


# `split_articles` takes the downloaded HTML text and pulls out each course card from the SEAS courses page. Specifically, it finds every \<article ...> block whose HTML class contains course-teaser.
def split_articles(markup: str) -> list[str]:
    return re.findall(r"<article\b[^>]*course-teaser[^>]*>.*?</article>", markup, flags=re.I | re.S)


def first_match(pattern: str, text: str, flags: int = re.I | re.S) -> str:
    match = re.search(pattern, text, flags=flags)
    if not match:
        return ""
    return normalize_space(html.unescape(match.group(1)))


# `parse_term_from_locator` extracts the academic term from a URL.
def parse_term_from_locator(locator_url: str) -> str:
    match = re.search(r"/(\d{4})/(fall|spring)/", locator_url, flags=re.I)
    if not match:
        return ""
    return f"{match.group(1)} {match.group(2).title()}"


# `parse_course_id` extracts Harvard’s course ID. It first looks inside the HTML for SearchText. The backup option is from the URL.
def parse_course_id(article: str, locator_url: str) -> str:
    search_text = first_match(r"SearchText&quot;:&quot;(\d+)&quot;", article)
    if search_text:
        return search_text
    match = re.search(r"colgsas-(\d+)", locator_url)
    return match.group(1) if match else ""


def department_for(subject_catalog: str) -> str:
    subject = subject_catalog.split(" ", 1)[0]
    return {
        "APCOMP": "Applied Computation",
        "APMTH": "Applied Mathematics",
        "COMPSCI": "Computer Science",
        "STAT": "Statistics",
    }.get(subject, "")


def requirement_area_for(subject_catalog: str) -> str:
    return {
        "APCOMP 209A": "Data Science/Machine Learning",
        "APCOMP 209B": "Data Science/Machine Learning",
        "APCOMP 215": "Computing",
        "APCOMP 221": "Ethics",
        "APCOMP 297R": "Research Experience",
    }.get(subject_catalog, "Additional technical/free elective")


# This function reads the HTML that is saved locally. Splits the page into individual course card HTML blocks. Extracts the relevant fields from each card, and builds a CourseRecord for each course card.
def parse_seas_courses(page: SourcePage, dataset_version: str, retrieved_at: str) -> list[CourseRecord]:
    markup = read_cached_text(page)
    records: list[CourseRecord] = []
    for article in split_articles(markup):
        title = first_match(r'<span class="course__title[^"]*">(.*?)</span>', article)
        subject_catalog = first_match(r"<strong>\s*([A-Z]+ [0-9A-Z]+)\s*</strong>", article)
        locator_url = first_match(r"""href=['"](https://locator\.tlt\.harvard\.edu/course/[^'"]+)['"]""", article)
        course_id = parse_course_id(article, locator_url)
        term = parse_term_from_locator(locator_url)
        description_html = first_match(r'<div class="course-teaser__body">(.*?)</div>', article)
        description = strip_tags(description_html)
        strong_values = re.findall(r"<strong>\s*(.*?)\s*</strong>", article, flags=re.I | re.S)
        instructors = strip_tags(strong_values[1]) if len(strong_values) > 1 else ""
        info_text = strip_tags(first_match(r'<div class="course-teaser__info">(.*?)</div>', article))
        meeting_days = ""
        meeting_time = ""
        for possible_days in ("Monday, Wednesday", "Tuesday, Thursday", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday"):
            if possible_days in info_text:
                meeting_days = possible_days.replace(", ", "; ")
                break
        time_match = re.search(r"\b\d{1,2}:\d{2}(?:am|pm)\s+to\s+\d{1,2}:\d{2}(?:am|pm)\b", info_text, flags=re.I)
        if time_match:
            meeting_time = normalize_space(time_match.group(0).replace(" to ", "-"))

        missing = []
        for field_name, value in {
            "course_id": course_id,
            "subject_catalog": subject_catalog,
            "title": title,
            "term": term,
            "description": description,
        }.items():
            if not value:
                missing.append(field_name)

        if not subject_catalog:
            continue

        records.append(
            CourseRecord(
                dataset_version=dataset_version,
                retrieved_at=retrieved_at,
                course_key=f"{subject_catalog}|{term}",
                course_id=course_id,
                course_id_type="numeric_harvard_course_id" if course_id else "",
                subject_catalog=subject_catalog,
                title=title,
                school="Harvard University",
                department=department_for(subject_catalog),
                term=term,
                credits=4,
                instructors=instructors,
                meeting_days=meeting_days,
                meeting_time=meeting_time,
                requirement_area=requirement_area_for(subject_catalog),
                description=description,
                source_urls="; ".join([url for url in (SEAS_COURSES_URL, locator_url, DEGREE_REQUIREMENTS_URL) if url]),
                missing_or_uncertain_fields="; ".join(missing),
            )
        )
    return records


# Loads previously saved JSON datasets and returns CourseRecord objects.
def load_snapshot(path: Path, dataset_version: str, retrieved_at: str) -> list[CourseRecord]:
    rows = json.loads(path.read_text())
    records: list[CourseRecord] = []
    for row in rows:
        normalized: dict[str, Any] = {column: row.get(column, "") for column in OUTPUT_COLUMNS}
        normalized["dataset_version"] = dataset_version
        normalized["retrieved_at"] = retrieved_at
        records.append(CourseRecord(**normalized))
    return records


def completeness_score(record: CourseRecord) -> tuple[int, int]:
    missing_count = len([part for part in record.missing_or_uncertain_fields.split("; ") if part])
    source_score = 0 if SEAS_COURSES_URL in record.source_urls else 1
    return missing_count, source_score


def dedupe(records: list[CourseRecord]) -> list[CourseRecord]:
    by_key: dict[str, CourseRecord] = {}
    for record in records:
        existing = by_key.get(record.course_key)
        if existing is None or completeness_score(record) < completeness_score(existing):
            by_key[record.course_key] = record
    return sorted(
        by_key.values(),
        key=lambda record: (record.requirement_area, record.subject_catalog, record.term),
    )


def trim_records(records: list[CourseRecord], max_rows: int) -> list[CourseRecord]:
    return records[:max_rows]


def write_csv(path: Path, records: list[CourseRecord]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("harvard_msds_courses"))
    parser.add_argument("--version", default="v0.4")
    parser.add_argument("--retrieved-at", default=date.today().isoformat())
    parser.add_argument("--max-rows", type=int, default=50)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--snapshot-json", type=Path, default=Path("harvard_msds_courses/v0.2_processed_2026-10-08.json"))
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = args.out_dir / f"{args.version}_raw_source_cache_{args.retrieved_at}"

    source_pages = [
        fetch_url(DEGREE_REQUIREMENTS_URL, cache_dir, args.refresh),
        fetch_url(SEAS_COURSES_URL, cache_dir, args.refresh),
    ]
    seas_records = parse_seas_courses(source_pages[1], args.version, args.retrieved_at)
    snapshot_records = load_snapshot(args.snapshot_json, args.version, args.retrieved_at)
    records = trim_records(dedupe([*seas_records, *snapshot_records]), args.max_rows)

    raw_payload = {
        "dataset_name": "harvard_seas_gsas_ms_data_science_courses",
        "dataset_version": args.version,
        "retrieved_at": args.retrieved_at,
        "scope": SCOPE,
        "source_strategy": (
            "Fetch and cache public Harvard SEAS pages where they are directly accessible. "
            "Normalize, dedupe, and version the final dataset."
        ),
        "source_pages": [asdict(page) for page in source_pages],
        "snapshot_json": str(args.snapshot_json),
        "live_seas_rows": len(seas_records),
        "snapshot_rows": len(snapshot_records),
        "processed_rows": len(records),
    }

    raw_path = args.out_dir / f"{args.version}_raw_{args.retrieved_at}.json"
    processed_csv_path = args.out_dir / f"{args.version}_processed_{args.retrieved_at}.csv"
    processed_json_path = args.out_dir / f"{args.version}_processed_{args.retrieved_at}.json"

    write_json(raw_path, raw_payload)
    write_json(processed_json_path, [asdict(record) for record in records])
    write_csv(processed_csv_path, records)

    print(f"Wrote {len(records)} processed records")
    print(f"Live SEAS rows: {len(seas_records)}")
    print(f"Snapshot rows: {len(snapshot_records)}")
    print(raw_path)
    print(processed_csv_path)
    print(processed_json_path)


if __name__ == "__main__":
    main()
