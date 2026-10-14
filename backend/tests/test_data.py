import pytest

from wayfind_retrieval.data import load_dataset, split_description, split_list
from tests.conftest import FIXTURE


def test_split_list_handles_semicolons_blanks_and_none():
    assert split_list("a; b ;; c") == ["a", "b", "c"]
    assert split_list("") == []
    assert split_list(None) == []


def test_split_description_separates_notes_and_course_site():
    summary, notes, site = split_description("Learn things. Notes: Formerly X. Course site: https://example.edu/x")
    assert (summary, notes, site) == ("Learn things.", "Formerly X.", "https://example.edu/x")
    assert split_description("Only a summary.") == ("Only a summary.", "", "")


def test_offerings_merge_into_one_course_per_catalog_number():
    courses = {c.course_id: c for c in load_dataset(FIXTURE).courses}
    assert sorted(courses) == ["TEST 101", "TEST 202", "TEST 303", "TEST 404"]  # blank row skipped
    capstone = courses["TEST 303"]
    assert capstone.terms == ["2026 Fall", "2027 Spring"]
    assert capstone.instructors == ["Edsger Dijkstra", "Barbara Liskov"]
    assert capstone.source_urls == ["https://example.edu/catalog/303"]


def test_course_site_becomes_a_source_and_fields_become_lists():
    courses = {c.course_id: c for c in load_dataset(FIXTURE).courses}
    assert courses["TEST 101"].source_urls[-1] == "https://example.edu/test-101"
    assert courses["TEST 101"].notes == "Formerly TEST 100."
    assert courses["TEST 202"].missing_or_uncertain_fields == ["meeting_days", "meeting_time"]
    assert courses["TEST 202"].harvard_course_id == "900202"


def test_missing_description_is_flagged_not_invented():
    course = next(c for c in load_dataset(FIXTURE).courses if c.course_id == "TEST 404")
    assert course.summary == ""
    assert course.missing_or_uncertain_fields == ["instructors", "description"]


def test_version_falls_back_to_content_hash_and_override_wins():
    dataset = load_dataset(FIXTURE)
    assert dataset.version == f"sha256-{dataset.sha256[:12]}"
    assert load_dataset(FIXTURE, version="v1.0").version == "v1.0"


def test_version_column_in_csv_is_used(tmp_path):
    path = tmp_path / "versioned.csv"
    path.write_text("dataset_version,subject_catalog,title,description\nv0.4,X 1,Title,Text.\n")
    assert load_dataset(path).version == "v0.4"


def test_missing_required_columns_fail_clearly(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("subject_catalog,title\nX 1,Title\n")
    with pytest.raises(ValueError, match="description"):
        load_dataset(path)
