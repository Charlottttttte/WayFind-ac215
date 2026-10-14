"""Query -> retrieved context.

Chroma returns chunks; users want courses. We over-fetch chunks, keep each course's
best-scoring chunk (max-pooling), and return that chunk's text as the supporting context.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from .config import Settings
from .data import Course
from .embeddings import Embedder, make_embedder
from .index import COLLECTION, chroma_client, ensure_index, load_courses, read_manifest

CHUNKS_PER_RESULT = 10


@dataclass
class Hit:
    course: Course
    score: float  # cosine similarity of the best matching chunk, in [-1, 1]
    context: str
    chunk_id: str  # the chunk that matched, e.g. "STAT 220#0"


class Retriever:
    def __init__(self, index_dir: Path, embedder: Embedder, min_score: float = 0.0) -> None:
        self.manifest = read_manifest(index_dir)
        if self.manifest is None:
            raise FileNotFoundError(f"No index manifest in {index_dir}; build the index first")
        if self.manifest["embedding_model"] != embedder.name:
            raise ValueError(
                f"Index was built with {self.manifest['embedding_model']!r}, query embedder is {embedder.name!r}"
            )
        self.embedder = embedder
        self.min_score = min_score
        self.courses = load_courses(index_dir)
        self.collection = chroma_client(index_dir).get_collection(COLLECTION)

    @property
    def dataset_version(self) -> str:
        return self.manifest["dataset_version"]

    def search(self, query: str, top_k: int = 5) -> list[Hit]:
        total = self.collection.count()
        if total == 0:
            return []
        result = self.collection.query(
            query_embeddings=self.embedder.embed([query]),
            n_results=min(total, top_k * CHUNKS_PER_RESULT),
            include=["metadatas", "distances"],  # ids are always returned
        )
        hits: dict[str, Hit] = {}
        for chunk_id, metadata, distance in zip(result["ids"][0], result["metadatas"][0], result["distances"][0]):
            score = 1.0 - distance
            course_id = metadata["course_id"]
            if score < self.min_score or course_id in hits:
                continue  # results arrive best-first, so the first chunk seen is the course's best
            hits[course_id] = Hit(self.courses[course_id], score, metadata["body"], chunk_id)
            if len(hits) == top_k:
                break
        return list(hits.values())


def main(argv: list[str] | None = None) -> None:
    """Print retrieval results for one query as JSON: ``python -m wayfind_retrieval.search "query"``."""
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit('usage: python -m wayfind_retrieval.search "query text" [top_k]')
    settings = Settings.from_env()
    embedder = make_embedder(settings.embedder)
    ensure_index(settings, embedder)
    retriever = Retriever(settings.index_dir, embedder, settings.min_score)
    hits = retriever.search(args[0], int(args[1]) if len(args) > 1 else 5)
    print(json.dumps({
        "query": args[0],
        "dataset_version": retriever.dataset_version,
        "embedding_model": embedder.name,
        "results": [
            {"rank": rank, "course_id": h.course.course_id, "title": h.course.title,
             "score": round(h.score, 4), "chunk_id": h.chunk_id, "context": h.context}
            for rank, h in enumerate(hits, 1)
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
