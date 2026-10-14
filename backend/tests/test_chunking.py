from wayfind_retrieval.chunking import chunk_course, sentence_windows, split_sentences
from wayfind_retrieval.data import Course


def make_course(**overrides) -> Course:
    fields = dict(course_id="TEST 1", title="Title", summary="One. Two.", notes="", description="One. Two.")
    return Course(**(fields | overrides))


def test_split_sentences():
    assert split_sentences("First one. Second? Third!") == ["First one.", "Second?", "Third!"]
    assert split_sentences("  ") == []


def test_short_text_is_one_window():
    assert sentence_windows("A b c. D e f.", max_words=50) == ["A b c. D e f."]


def test_long_text_splits_with_one_sentence_overlap():
    text = "A a a a. B b b b. C c c c. D d d d."
    assert sentence_windows(text, max_words=8) == ["A a a a. B b b b.", "B b b b. C c c c.", "C c c c. D d d d."]


def test_oversized_sentence_is_kept_whole():
    long_sentence = "Long " + " ".join(["word"] * 20) + "."
    assert sentence_windows("Short one. " + long_sentence, max_words=10) == ["Short one.", long_sentence]


def test_abbreviations_do_not_end_sentences():
    assert split_sentences("Methods, e.g. trees and boosting. Next topic.") == [
        "Methods, e.g. trees and boosting.", "Next topic."
    ]


def test_long_description_gets_stable_chunk_ids_and_shared_header():
    course = make_course(summary="A a a a. B b b b. C c c c.", requirement_area="Statistics elective")
    chunks = chunk_course(course, max_words=8)
    assert [c.chunk_id for c in chunks] == ["TEST 1#0", "TEST 1#1"]
    assert {c.header for c in chunks} == {"TEST 1: Title (Statistics elective)."}


def test_embedding_text_carries_course_identity_but_body_does_not():
    chunk = chunk_course(make_course())[0]
    assert chunk.embedding_text == "TEST 1: Title. One. Two."
    assert chunk.body == "One. Two."


def test_notes_are_not_embedded():
    chunks = chunk_course(make_course(notes="Meets in room 223."))
    assert all("room 223" not in c.embedding_text for c in chunks)


def test_course_without_description_is_indexed_by_header_only():
    [chunk] = chunk_course(make_course(summary=""))
    assert chunk.body == "" and chunk.embedding_text == "TEST 1: Title."
