"""Build the Chroma vector index from the course dataset.

Run: ``python -m wayfind_retrieval.index [--force]``

The index directory is self-contained. Its ``active/`` subdirectory holds the Chroma store, a snapshot of the course records
(``courses.json``), and ``manifest.json`` recording the dataset version, the SHA-256 of the
input file, the embedding model, and the chunking settings. An existing index is reused only
if all of those still match; otherwise it is rebuilt.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import chromadb

from .chunking import chunk_courses
from .config import Settings
from .data import Course, load_dataset
from .embeddings import Embedder, make_embedder

COLLECTION = "courses"
MANIFEST = "manifest.json"
COURSES = "courses.json"
CHROMA_DIR = "chroma"
ACTIVE = "active"
STAGING = "staging"
log = logging.getLogger("wayfind.index")


def chroma_client(index_dir: Path) -> chromadb.ClientAPI:
    return chromadb.PersistentClient(
        path=str(index_dir / ACTIVE / CHROMA_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    )


def read_manifest(index_dir: Path) -> dict | None:
    try:
        return json.loads((index_dir / ACTIVE / MANIFEST).read_text())
    except (OSError, ValueError):
        return None


def expected_manifest(settings: Settings, embedder: Embedder) -> dict:
    dataset = load_dataset(settings.data_path, settings.dataset_version)
    return {
        "dataset_version": dataset.version,
        "dataset_sha256": dataset.sha256,
        "embedding_model": embedder.name,
        "max_chunk_words": settings.max_chunk_words,
    }


def is_current(settings: Settings, embedder: Embedder) -> bool:
    manifest = read_manifest(settings.index_dir)
    if manifest is None:
        return False
    expected = expected_manifest(settings, embedder)
    return all(manifest.get(key) == value for key, value in expected.items())


def build_index(settings: Settings, embedder: Embedder) -> dict:
    """Load, chunk, embed and store the dataset; return the manifest that was written."""
    dataset = load_dataset(settings.data_path, settings.dataset_version)
    if not dataset.courses:
        raise ValueError(f"No courses found in {settings.data_path}")
    chunks = chunk_courses(dataset.courses, settings.max_chunk_words)
    texts = [chunk.embedding_text for chunk in chunks]
    log.info("Embedding %d chunks from %d courses with %s", len(chunks), len(dataset.courses), embedder.name)
    vectors = embedder.embed(texts)

    # Build into a staging directory, then swap, so a failed build never leaves a half-written
    # index. Both live inside index_dir because in a container index_dir is a mounted volume.
    staging = settings.index_dir / STAGING
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    collection = chromadb.PersistentClient(
        path=str(staging / CHROMA_DIR), settings=chromadb.Settings(anonymized_telemetry=False)
    ).create_collection(
        COLLECTION,
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
    )
    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"course_id": c.course_id, "body": c.body} for c in chunks],
    )
    manifest = {
        "dataset_version": dataset.version,
        "dataset_sha256": dataset.sha256,
        "dataset_path": str(settings.data_path),
        "embedding_model": embedder.name,
        "embedding_dimensions": len(vectors[0]),
        "distance": "cosine",
        "max_chunk_words": settings.max_chunk_words,
        "courses": len(dataset.courses),
        "chunks": len(chunks),
        "courses_without_description": sum(not c.summary for c in dataset.courses),
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (staging / COURSES).write_text(json.dumps([asdict(c) for c in dataset.courses], indent=2))
    (staging / MANIFEST).write_text(json.dumps(manifest, indent=2))

    active = settings.index_dir / ACTIVE
    shutil.rmtree(active, ignore_errors=True)
    staging.rename(active)
    log.info("Index written to %s (dataset %s)", settings.index_dir, dataset.version)
    return manifest


def ensure_index(settings: Settings, embedder: Embedder, force: bool = False) -> dict:
    if not force and is_current(settings, embedder):
        log.info("Index in %s is current; reusing it", settings.index_dir)
        return read_manifest(settings.index_dir)
    return build_index(settings, embedder)


def load_courses(index_dir: Path) -> dict[str, Course]:
    records = json.loads((index_dir / ACTIVE / COURSES).read_text())
    return {record["course_id"]: Course(**record) for record in records}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the WayFind course vector index.")
    parser.add_argument("--force", action="store_true", help="rebuild even if the index is current")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
    manifest = ensure_index(settings, make_embedder(settings.embedder), force=args.force)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
