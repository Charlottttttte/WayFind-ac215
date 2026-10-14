from pathlib import Path

import pytest

from wayfind_retrieval.config import Settings
from wayfind_retrieval.embeddings import HashingEmbedder
from wayfind_retrieval.index import build_index

FIXTURE = Path(__file__).parent / "fixtures" / "courses.csv"


@pytest.fixture
def settings(tmp_path) -> Settings:
    # Hashing embedder: deterministic and offline. Real-model behavior is checked in the container smoke test.
    return Settings(data_path=FIXTURE, index_dir=tmp_path / "index", embedder="hashing", min_score=0.0)


@pytest.fixture
def embedder() -> HashingEmbedder:
    return HashingEmbedder()


@pytest.fixture
def built(settings, embedder) -> Settings:
    build_index(settings, embedder)
    return settings
