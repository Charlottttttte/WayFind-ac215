# WayFind MS2 retrieval backend

Owner: Shravya. This component implements the MS2 RAG retrieval slice: course data → chunks → embeddings → Chroma vector index → `POST /search`, returning matching courses with the retrieved passage and sources. It serves the response shape in [frontend/API_CONTRACT.md](../frontend/API_CONTRACT.md).

Planning, prerequisite checking, trained ranking, LLM interpretation, and mentor matching are outside MS2. Results are similarity matches, not degree advice.

## Pipeline

```
data/<courses>.csv ──load──> 1 record per course ──chunk──> sentence windows ──embed──> Chroma (cosine)
   (John's ingestion)        (offerings merged)            + course header        MiniLM-L6-v2 (ONNX)
                                                                                         │
            query ──embed──> top chunks ──max-pool per course──> top_k courses + best passage ──> /search
```

| Step | Module | What it does |
| --- | --- | --- |
| Load | [data.py](wayfind_retrieval/data.py) | Reads the processed CSV, merges offerings of one catalog number (e.g. APCOMP 297R Fall + Spring) into one course, converts semicolon-delimited fields to lists, moves the `Course site:` URL into `source_urls`, and separates catalog notes from the description. |
| Chunk | [chunking.py](wayfind_retrieval/chunking.py) | Splits each description into windows of at most 120 words on sentence boundaries, with one sentence of overlap, and prefixes each with `CODE: Title (requirement area).` |
| Embed | [embeddings.py](wayfind_retrieval/embeddings.py) | `all-MiniLM-L6-v2` (384-d) through ONNX Runtime, using Chroma's bundled copy. No PyTorch, GPU, or API key. |
| Index | [index.py](wayfind_retrieval/index.py) | Writes the Chroma store, a `courses.json` snapshot, and `manifest.json` (dataset version, SHA-256 of the input file, model, chunk settings, counts). Reuses the index only when all of these still match; builds into a staging directory so a failed build keeps the previous index. |
| Search | [search.py](wayfind_retrieval/search.py) | Embeds the query, fetches `10 × top_k` chunks, keeps each course's best chunk, drops matches below `WAYFIND_MIN_SCORE`, and returns courses in score order. |
| Serve | [api.py](wayfind_retrieval/api.py) | FastAPI `POST /search` and `GET /health`. Loads the model and index once at startup. |
| Evaluate | [evaluate.py](wayfind_retrieval/evaluate.py) | hit@k, MRR, and NDCG@k over labeled queries. This is the embedding-similarity baseline the MS3 ranker must beat (proposal objective O3). |

### Design decisions

- **Retrieval unit is the course, not the chunk.** Chroma ranks chunks; showing three chunks of one course as three results would be wrong. Max-pooling keeps the best chunk per course and returns it as the supporting `context`.
- **Only descriptions are embedded.** The first version also embedded catalog notes and a requirement-area/instructor chunk. On real queries those short chunks were dominated by the course header, behaved like title matches, and outranked the description, so the returned "context" was boilerplate such as room numbers. The requirement area now lives in the header of every chunk, so queries like "statistics elective" still match. Notes stay on the record for MS3 prerequisite parsing.
- **Why chunk 100-word descriptions?** The median description is 103 words and the longest 223, so most courses are one chunk (36 courses → 46 chunks). Windowing matters for the long ones and for MS3 sources such as faculty pages and publications. The header keeps every chunk attributable to its course.
- **Local ONNX MiniLM.** It is free, deterministic, runs offline, and is baked into the image at build time, so containers never download a model at query time. A Vertex AI embedding model can replace it in MS3 by adding an embedder. The manifest records the model, and an index built with one model refuses queries from another.
- **Minimum score 0.25.** With MiniLM on this dataset, nonsense input scored at most 0.15–0.20, while relevant top matches scored 0.29–0.73. The threshold is set from about ten smoke queries, not a labeled set; revisit it when acceptance labels exist. It does **not** produce empty results for queries in the frontend's labeled profile format, because the label text alone scores up to 0.37 (see [retrieval evidence](../docs/ms2/retrieval-evidence.md#observed-failures), failure 6).
- **Course ID.** `course_id` is the catalog code (`APCOMP 209A`), which students recognize and the acceptance queries use. The numeric Harvard ID is returned as `harvard_course_id`.
- **Privacy.** Queries contain student background, so logs record only query length, result IDs, and latency.

## Data and versioning

The input is John's processed course CSV. Required columns: `subject_catalog`, `title`, `description`. Optional columns pass through when present: `term`, `instructors`, `source_urls`, `requirement_area`, `retrieved_at`, `missing_or_uncertain_fields`, `dataset_version`, `course_id`.

`dataset_version` resolves in this order: `WAYFIND_DATASET_VERSION` → the CSV's `dataset_version` column, if it has a single value → `sha256-<first 12 hex chars of the file>`. The full SHA-256 is always recorded in `manifest.json` and reported by `/health`, so every response traces to one exact input file.

The data file is not part of this component. As of this PR, John's 36-course CSV (`data/scraped_sheet1.csv`) is in PR #2 and not yet on `main`. Unit tests and CI use the synthetic fixture [tests/fixtures/courses.csv](tests/fixtures/courses.csv) (invented `TEST` courses).

## Run

### Docker (recommended)

From this directory, with the course CSV in the repository's `data/` folder:

```sh
docker compose up --build
```

`indexer` builds the index into a named volume and exits. `backend` then starts on http://127.0.0.1:8000. Copy `.env.example` to `.env` to change the port, data file, version label, or score threshold. Stop with `docker compose down`; add `-v` to delete the index volume.

For the repository-wide pipeline, reuse both services with build context `./backend`. Mount `data/` read-only at `/data`, share a volume at `/index`, and start `backend` after `indexer` completes. The frontend reaches it at `SEARCH_API_URL=http://backend:8000/search`.

### Local Python

Requires [uv](https://docs.astral.sh/uv/). It installs Python 3.12 if needed.

```sh
uv sync
uv run python -m wayfind_retrieval.index           # build or reuse the index; prints the manifest
uv run python -m wayfind_retrieval.search "Bayesian statistics" 5   # one query, JSON output
uv run python -m wayfind_retrieval.api             # http://127.0.0.1:8000
uv run python -m wayfind_retrieval.evaluate queries.json --k 5 --out report.json
```

The first local run downloads the 79 MB model to `~/.cache/chroma`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `WAYFIND_DATA_PATH` | `../data/scraped_sheet1.csv` (`/data/scraped_sheet1.csv` in Docker) | Course CSV to index |
| `WAYFIND_INDEX_DIR` | `backend/.index` (`/index` in Docker) | Index location |
| `WAYFIND_DATASET_VERSION` | — | Version label override |
| `WAYFIND_MIN_SCORE` | `0.25` | Cosine-similarity cutoff |
| `WAYFIND_MAX_CHUNK_WORDS` | `120` | Chunk window size; changing it triggers a rebuild |
| `WAYFIND_EMBEDDER` | `minilm` | `hashing` is a test-only offline embedder |
| `HOST`, `PORT` | `127.0.0.1`, `8000` (`0.0.0.0` in Docker) | API bind address |

## API

`POST /search` with body `{"query": "<text>", "top_k": 5}`. `query` is required, non-blank, and at most 4,000 characters; `top_k` is 1–20 (default 5).

```json
{
  "dataset_version": "sha256-09fc6649582f",
  "embedding_model": "all-MiniLM-L6-v2 (onnx)",
  "results": [{
    "course_id": "STAT 120",
    "title": "Introduction to Bayesian Inference and Applications",
    "term": "2026 Fall",
    "description": "<full catalog text>",
    "context": "<the description passage that matched>",
    "source_urls": ["https://www.coursicle.com/harvard/courses/STAT/120/", "..."],
    "retrieved_at": "2026-10-08",
    "missing_or_uncertain_fields": [],
    "score": 0.6213,
    "chunk_id": "STAT 120#0",
    "requirement_area": "Statistics elective",
    "harvard_course_id": "156425"
  }]
}
```

Fields beyond the contract (`embedding_model`, `score`, `chunk_id`, `requirement_area`, `harvard_course_id`) are ignored by the current frontend. `term` joins multiple offerings with `; `.

| Status | When |
| --- | --- |
| 200 with `results: []` | No course scores above the threshold |
| 422 | Missing, blank, or oversized query, or `top_k` out of range |
| 503 `{"error": "Search service unavailable"}` | Retrieval raised an error; details go to the server log only |

`GET /health` returns `status`, `component`, `dataset_version`, `embedding_model`, `courses`, and `chunks`. The container healthcheck uses it.

## Tests

```sh
uv run pytest --cov --cov-report=term-missing
```

46 tests, 95% line coverage. They cover CSV parsing and offering merges, chunk windows, index reuse/rebuild/failure, best-chunk-per-course ranking, the score threshold, the API contract and errors, log privacy, and metric math. Tests use the hashing embedder and the synthetic fixture, so they run offline in about 1 second. CI also builds the Docker image and checks real-model retrieval on the fixture (see [docs/ci.md](../docs/ci.md)).

## Known limitations

See [docs/ms2/retrieval-evidence.md](../docs/ms2/retrieval-evidence.md) for example runs and observed failures. In short:

- **Profile-format queries compress scores.** The frontend sends labeled lines (`Interests:`, `Career goal:`, …). The labels add shared vocabulary, so all scores rise to about 0.45–0.55 and gaps between good and mediocre matches shrink. The proposal's LLM interpretation step (MS3) is the intended fix.
- **Completed courses are not excluded.** This follows the contract; filtering belongs to the MS3 planner.
- **Cross-listed duplicates.** APCOMP 209B and COMPSCI 1090B are the same course and both appear.
- **Coverage gaps follow the data.** The dataset has no finance courses, so quant-finance queries return weak, loosely related matches.
