"""Score retrieval against labeled queries: hit@k, MRR and NDCG@k.

Run: ``python -m wayfind_retrieval.evaluate path/to/queries.json [--k 5] [--out report.json]``

Queries file format::

    {"queries": [{"id": "q1", "query": "...", "relevant": ["APCOMP 209A", "STAT 139"]}]}

Relevance is binary. This is the embedding-similarity baseline that the MS3 trained ranker is
compared against (proposal objective O3), so the metric definitions must stay fixed.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .config import Settings
from .embeddings import make_embedder
from .index import ensure_index
from .search import Retriever


def hit_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(course in relevant for course in ranked[:k]) else 0.0


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for rank, course in enumerate(ranked, 1):
        if course in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    dcg = sum(1.0 / math.log2(rank + 1) for rank, course in enumerate(ranked[:k], 1) if course in relevant)
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def evaluate(retriever: Retriever, queries: list[dict], k: int = 5) -> dict:
    rows = []
    for item in queries:
        relevant = set(item["relevant"])
        ranked = [hit.course.course_id for hit in retriever.search(item["query"], k)]
        rows.append({
            "id": item["id"],
            "retrieved": ranked,
            "relevant": sorted(relevant),
            "unknown_relevant": sorted(relevant - retriever.courses.keys()),
            f"hit@{k}": hit_at_k(ranked, relevant, k),
            "rr": reciprocal_rank(ranked, relevant),
            f"ndcg@{k}": round(ndcg_at_k(ranked, relevant, k), 4),
        })
    mean = lambda key: round(sum(row[key] for row in rows) / len(rows), 4) if rows else 0.0
    return {
        "dataset_version": retriever.dataset_version,
        "embedding_model": retriever.embedder.name,
        "k": k,
        "queries": len(rows),
        f"hit@{k}": mean(f"hit@{k}"),
        "mrr": mean("rr"),
        f"ndcg@{k}": mean(f"ndcg@{k}"),
        "per_query": rows,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval on labeled queries.")
    parser.add_argument("queries", type=Path)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    embedder = make_embedder(settings.embedder)
    ensure_index(settings, embedder)
    queries = json.loads(args.queries.read_text())["queries"]
    report = evaluate(Retriever(settings.index_dir, embedder, settings.min_score), queries, args.k)
    text = json.dumps(report, indent=2)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
