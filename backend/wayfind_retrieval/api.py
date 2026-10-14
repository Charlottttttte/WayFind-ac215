"""HTTP API: ``POST /search`` and ``GET /health``.

The response shape follows ``frontend/API_CONTRACT.md``. Queries contain student profile text,
so logs record only query length, result IDs and latency, never the query itself.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from .config import Settings
from .embeddings import make_embedder
from .index import ensure_index
from .search import Hit, Retriever

log = logging.getLogger("wayfind.api")


class SearchRequest(BaseModel):
    query: str = Field(max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be blank")
        return value.strip()


class CourseResult(BaseModel):
    course_id: str
    title: str
    term: str
    description: str
    context: str
    source_urls: list[str]
    retrieved_at: str
    missing_or_uncertain_fields: list[str]
    score: float
    chunk_id: str
    requirement_area: str
    harvard_course_id: str


class SearchResponse(BaseModel):
    dataset_version: str
    embedding_model: str
    results: list[CourseResult]


def to_result(hit: Hit) -> CourseResult:
    course = hit.course
    return CourseResult(
        course_id=course.course_id,
        title=course.title,
        term="; ".join(course.terms),
        description=course.description,
        context=hit.context,
        source_urls=course.source_urls,
        retrieved_at=course.retrieved_at,
        missing_or_uncertain_fields=course.missing_or_uncertain_fields,
        score=round(hit.score, 4),
        chunk_id=hit.chunk_id,
        requirement_area=course.requirement_area,
        harvard_course_id=course.harvard_course_id,
    )


def create_app(settings: Settings | None = None, build_index: bool = True) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load the model and index once at startup, not per request.
        embedder = make_embedder(settings.embedder)
        if build_index:
            ensure_index(settings, embedder)
        app.state.retriever = Retriever(settings.index_dir, embedder, settings.min_score)
        log.info("Serving dataset %s", app.state.retriever.dataset_version)
        yield

    app = FastAPI(title="WayFind retrieval API", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    def health(request: Request) -> dict:
        manifest = request.app.state.retriever.manifest
        return {
            "status": "ok",
            "component": "backend",
            "dataset_version": manifest["dataset_version"],
            "embedding_model": manifest["embedding_model"],
            "courses": manifest["courses"],
            "chunks": manifest["chunks"],
        }

    @app.post("/search", response_model=SearchResponse)
    def search(body: SearchRequest, request: Request) -> SearchResponse | JSONResponse:
        retriever: Retriever = request.app.state.retriever
        started = time.perf_counter()
        try:
            hits = retriever.search(body.query, body.top_k)
        except Exception:
            log.exception("Search failed")
            return JSONResponse(status_code=503, content={"error": "Search service unavailable"})
        log.info(
            "search query_chars=%d top_k=%d results=%s latency_ms=%.0f",
            len(body.query), body.top_k, [h.course.course_id for h in hits],
            (time.perf_counter() - started) * 1000,
        )
        return SearchResponse(
            dataset_version=retriever.dataset_version,
            embedding_model=retriever.embedder.name,
            results=[to_result(hit) for hit in hits],
        )

    return app


def main() -> None:
    import os

    import uvicorn

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    uvicorn.run(create_app(), host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
