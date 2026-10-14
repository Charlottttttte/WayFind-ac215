import json
import math

import pytest

from wayfind_retrieval.evaluate import evaluate, hit_at_k, main, ndcg_at_k, reciprocal_rank
from wayfind_retrieval.search import Retriever


def test_hit_at_k():
    assert hit_at_k(["a", "b", "c"], {"c"}, k=3) == 1.0
    assert hit_at_k(["a", "b", "c"], {"c"}, k=2) == 0.0


def test_reciprocal_rank():
    assert reciprocal_rank(["a", "b", "c"], {"b", "c"}) == 0.5
    assert reciprocal_rank(["a"], {"z"}) == 0.0


def test_ndcg_perfect_partial_and_empty():
    assert ndcg_at_k(["a", "b"], {"a", "b"}, k=5) == 1.0
    assert ndcg_at_k(["x", "a"], {"a"}, k=5) == pytest.approx(1 / math.log2(3))
    assert ndcg_at_k(["x"], set(), k=5) == 0.0


def test_evaluate_reports_means_and_unknown_labels(built, embedder):
    queries = [
        {"id": "q1", "query": "bayesian priors posteriors", "relevant": ["TEST 101"]},
        {"id": "q2", "query": "transformers language models", "relevant": ["TEST 202", "NOT 999"]},
    ]
    report = evaluate(Retriever(built.index_dir, embedder), queries, k=3)
    assert report["queries"] == 2
    assert report["hit@3"] == 1.0
    assert report["per_query"][1]["unknown_relevant"] == ["NOT 999"]
    assert 0 < report["ndcg@3"] <= 1


def test_evaluate_cli_writes_report(built, tmp_path, monkeypatch):
    monkeypatch.setenv("WAYFIND_DATA_PATH", str(built.data_path))
    monkeypatch.setenv("WAYFIND_INDEX_DIR", str(built.index_dir))
    monkeypatch.setenv("WAYFIND_EMBEDDER", "hashing")
    monkeypatch.setenv("WAYFIND_MIN_SCORE", "0")
    queries = tmp_path / "queries.json"
    queries.write_text(json.dumps({"queries": [{"id": "q", "query": "capstone", "relevant": ["TEST 303"]}]}))
    out = tmp_path / "report.json"
    main([str(queries), "--k", "2", "--out", str(out)])
    assert json.loads(out.read_text())["hit@2"] == 1.0
