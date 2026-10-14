"""Runtime settings, read from environment variables so containers can override them."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BACKEND_DIR.parent


@dataclass(frozen=True)
class Settings:
    data_path: Path
    index_dir: Path
    embedder: str = "minilm"
    dataset_version: str | None = None
    max_chunk_words: int = 120
    min_score: float = 0.25

    @classmethod
    def from_env(cls) -> Settings:
        env = os.environ
        return cls(
            data_path=Path(env.get("WAYFIND_DATA_PATH", REPO_DIR / "data" / "scraped_sheet1.csv")),
            index_dir=Path(env.get("WAYFIND_INDEX_DIR", BACKEND_DIR / ".index")),
            embedder=env.get("WAYFIND_EMBEDDER", "minilm"),
            dataset_version=env.get("WAYFIND_DATASET_VERSION") or None,
            max_chunk_words=int(env.get("WAYFIND_MAX_CHUNK_WORDS", "120")),
            min_score=float(env.get("WAYFIND_MIN_SCORE", "0.25")),
        )
