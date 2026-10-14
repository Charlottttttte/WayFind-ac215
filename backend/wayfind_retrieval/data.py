"""Load the processed course CSV into one record per course.

The ingestion output has one row per offering (course x term). Retrieval works on courses,
so offerings of the same catalog number are merged and their terms listed together.
"""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_COLUMNS = {"subject_catalog", "title", "description"}
COURSE_SITE = re.compile(r"\s*Course site:\s*(\S+)\s*$")
NOTES = re.compile(r"\s*Notes:\s*")


@dataclass
class Course:
    course_id: str  # catalog code, e.g. "APCOMP 209A"
    title: str
    summary: str  # description without the "Notes:" and "Course site:" trailers
    notes: str
    description: str  # original catalog text, returned to the frontend
    requirement_area: str = ""
    department: str = ""
    harvard_course_id: str = ""
    terms: list[str] = field(default_factory=list)
    instructors: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    retrieved_at: str = ""
    missing_or_uncertain_fields: list[str] = field(default_factory=list)


@dataclass
class Dataset:
    courses: list[Course]
    version: str
    sha256: str
    path: Path


def split_list(value: str | None) -> list[str]:
    """Split the pipeline's semicolon-delimited fields into a clean list."""
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def merge_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def split_description(description: str) -> tuple[str, str, str]:
    """Return (summary, notes, course_site_url) from a catalog description."""
    text = description.strip()
    site = ""
    if match := COURSE_SITE.search(text):
        site = match.group(1)
        text = text[: match.start()].strip()
    summary, *notes = NOTES.split(text, maxsplit=1)
    return summary.strip(), notes[0].strip() if notes else "", site


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_dataset(path: Path, version: str | None = None) -> Dataset:
    """Read the course CSV and record which data version the index is built from.

    Version precedence: explicit override, then the CSV's own ``dataset_version`` column,
    then a content hash so every index can still be traced to its exact input file.
    """
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
        rows = list(reader)

    sha256 = file_sha256(path)
    csv_versions = {row.get("dataset_version", "").strip() for row in rows} - {""}
    if version is None and len(csv_versions) == 1:
        version = csv_versions.pop()
    version = version or f"sha256-{sha256[:12]}"

    courses: dict[str, Course] = {}
    for row in rows:
        course_id = row["subject_catalog"].strip()
        if not course_id or not row["title"].strip():
            continue
        summary, notes, site = split_description(row["description"])
        course = courses.get(course_id)
        if course is None:
            course = courses[course_id] = Course(
                course_id=course_id,
                title=row["title"].strip(),
                summary=summary,
                notes=notes,
                description=row["description"].strip(),
                requirement_area=row.get("requirement_area", "").strip(),
                department=row.get("department", "").strip(),
                harvard_course_id=row.get("course_id", "").strip(),
                retrieved_at=row.get("retrieved_at", "").strip(),
            )
        merge_unique(course.terms, split_list(row.get("term")))
        merge_unique(course.instructors, split_list(row.get("instructors")))
        merge_unique(course.source_urls, split_list(row.get("source_urls")) + ([site] if site else []))
        merge_unique(course.missing_or_uncertain_fields, split_list(row.get("missing_or_uncertain_fields")))
        if not course.summary:
            merge_unique(course.missing_or_uncertain_fields, ["description"])

    return Dataset(courses=list(courses.values()), version=version, sha256=sha256, path=path)
