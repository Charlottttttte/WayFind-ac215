from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from wayfind_retrieval.api import create_app

CONTRACT_FIELDS = {
    "course_id", "title", "term", "description", "context",
    "source_urls", "retrieved_at", "missing_or_uncertain_fields",
}


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:  # startup builds the index
        yield client


def test_health_reports_dataset_and_index(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["component"] == "backend"
    assert body["dataset_version"].startswith("sha256-")
    assert body["courses"] == 4


def test_search_matches_frontend_contract(client):
    response = client.post("/search", json={"query": "deep learning for language", "top_k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["dataset_version"].startswith("sha256-")
    assert 0 < len(body["results"]) <= 3
    for result in body["results"]:
        assert CONTRACT_FIELDS <= result.keys()
        assert result["course_id"].strip() and result["title"].strip()
        assert isinstance(result["source_urls"], list)
        assert isinstance(result["missing_or_uncertain_fields"], list)
    assert body["results"][0]["course_id"] == "TEST 202"


def test_merged_offerings_list_all_terms(client):
    body = client.post("/search", json={"query": "capstone project industry partner", "top_k": 1}).json()
    assert body["results"][0]["course_id"] == "TEST 303"
    assert body["results"][0]["term"] == "2026 Fall; 2027 Spring"


def test_frontend_profile_query_is_accepted(client):
    query = "Interests: bayesian inference\nCareer goal: PhD / research\nCompleted courses: TEST 303"
    response = client.post("/search", json={"query": query, "top_k": 5})
    assert response.status_code == 200
    assert response.json()["results"][0]["course_id"] == "TEST 101"


def test_top_k_defaults_to_five(client):
    assert len(client.post("/search", json={"query": "course"}).json()["results"]) <= 5


@pytest.mark.parametrize("payload", [
    {"query": "   "},
    {"query": ""},
    {"top_k": 5},
    {"query": "ml", "top_k": 0},
    {"query": "ml", "top_k": 21},
    {"query": "x" * 4001},
])
def test_invalid_requests_are_rejected(client, payload):
    assert client.post("/search", json=payload).status_code == 422


def test_no_match_returns_empty_results(settings):
    with TestClient(create_app(replace(settings, min_score=0.99))) as client:
        body = client.post("/search", json={"query": "zzz qqq", "top_k": 5}).json()
    assert body["results"] == []


def test_retrieval_failure_returns_503_without_details(client, monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("vector store down at /secret/path")

    monkeypatch.setattr(client.app.state.retriever, "search", broken)
    response = client.post("/search", json={"query": "ml"})
    assert response.status_code == 503
    assert response.json() == {"error": "Search service unavailable"}


def test_logs_do_not_contain_query_text(client, caplog):
    caplog.set_level("INFO", logger="wayfind.api")
    client.post("/search", json={"query": "my private background details"})
    assert "private background" not in caplog.text
    assert "query_chars=" in caplog.text
