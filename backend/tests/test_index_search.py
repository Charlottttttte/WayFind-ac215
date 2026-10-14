import json
from dataclasses import replace

import pytest

from wayfind_retrieval.embeddings import HashingEmbedder, make_embedder
from wayfind_retrieval.index import ensure_index, is_current, read_manifest
from wayfind_retrieval.search import Retriever


def test_manifest_records_version_hash_model_and_counts(built):
    manifest = read_manifest(built.index_dir)
    assert manifest["dataset_version"].startswith("sha256-")
    assert len(manifest["dataset_sha256"]) == 64
    assert manifest["embedding_model"] == "hashing-256"
    assert manifest["courses"] == 4
    assert manifest["chunks"] == 4  # fixture descriptions are short: one chunk per course
    assert manifest["courses_without_description"] == 1


def test_index_is_reused_when_current_and_rebuilt_when_inputs_change(built, embedder, tmp_path):
    built_at = read_manifest(built.index_dir)["built_at"]
    assert is_current(built, embedder)
    assert ensure_index(built, embedder)["built_at"] == built_at

    assert not is_current(built, HashingEmbedder(dimensions=64))  # different model
    assert not is_current(replace(built, max_chunk_words=10), embedder)  # different chunking

    changed = tmp_path / "changed.csv"
    changed.write_text(built.data_path.read_text().replace("Bayesian", "Frequentist"))
    assert not is_current(replace(built, data_path=changed), embedder)  # different data


def test_failed_build_keeps_previous_index(built, embedder, tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("subject_catalog,title,description\n")
    with pytest.raises(ValueError, match="No courses"):
        ensure_index(replace(built, data_path=empty), embedder)
    assert read_manifest(built.index_dir)["courses"] == 4


def test_search_returns_one_result_per_course_best_first(built, embedder):
    hits = Retriever(built.index_dir, embedder).search("bayesian inference with priors and posteriors", top_k=4)
    ids = [hit.course.course_id for hit in hits]
    assert ids[0] == "TEST 101"
    assert len(ids) == len(set(ids))
    assert [hit.score for hit in hits] == sorted((hit.score for hit in hits), reverse=True)
    assert "Bayesian" in hits[0].context or "posteriors" in hits[0].context


def test_top_k_limits_results(built, embedder):
    assert len(Retriever(built.index_dir, embedder).search("course", top_k=2)) == 2


def test_min_score_filters_weak_matches(built, embedder):
    assert Retriever(built.index_dir, embedder, min_score=0.99).search("unrelated words", top_k=5) == []


def test_retriever_requires_index_and_matching_model(built, settings, tmp_path):
    with pytest.raises(FileNotFoundError):
        Retriever(tmp_path / "missing", HashingEmbedder())
    with pytest.raises(ValueError, match="hashing-256"):
        Retriever(built.index_dir, HashingEmbedder(dimensions=64))


def test_make_embedder_rejects_unknown_names():
    assert make_embedder("hashing").name == "hashing-256"
    with pytest.raises(ValueError):
        make_embedder("nope")


def test_hashing_embedder_is_deterministic_and_normalized():
    first, second = HashingEmbedder().embed(["same text", "same text"])
    assert first == second
    assert sum(value * value for value in first) == pytest.approx(1.0)


def test_search_cli_prints_json(built, monkeypatch, capsys):
    from wayfind_retrieval import search

    monkeypatch.setenv("WAYFIND_DATA_PATH", str(built.data_path))
    monkeypatch.setenv("WAYFIND_INDEX_DIR", str(built.index_dir))
    monkeypatch.setenv("WAYFIND_EMBEDDER", "hashing")
    monkeypatch.setenv("WAYFIND_MIN_SCORE", "0")
    search.main(["language models and transformers", "2"])
    output = json.loads(capsys.readouterr().out)
    assert output["results"][0]["course_id"] == "TEST 202"
    assert len(output["results"]) == 2
