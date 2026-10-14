# MS2 retrieval evidence

Owner: Shravya. These are runs of the containerized retrieval pipeline on real course data, from query to retrieved context, covering the MS2 requirement for "evidence of one end-to-end retrieval example."

| Item | Value |
| --- | --- |
| Base commit | `ee6a04ba8f0e18db65642f5402380ea8694db623` (`main`) plus the backend branch |
| Dataset | John's `data/scraped_sheet1.csv` from PR #2 (not yet on `main`); 37 rows → 36 courses |
| Dataset version | `sha256-09fc6649582f` (SHA-256 `09fc6649582ff140cab0e50a7fdfe555cf80c2b1d4de7758ad94b1e8e8d20b88`) |
| Model | `all-MiniLM-L6-v2` (ONNX, 384-d), cosine distance |
| Index | 46 chunks from 36 courses, 120-word windows |
| Environment | Docker Desktop 28.3.2 on macOS (arm64), image `wayfind-backend:local`, 2026-10-14 |

## Pipeline run

```sh
cd backend && docker compose up --build
```

The `indexer` service builds the index and exits; `backend` then serves on port 8000. The index build was rerun with `--network none` to show that the embedding model is baked into the image: [index-build.log](retrieval-logs/index-build.log). One full API response is in [search-response.json](retrieval-logs/search-response.json).

`/health`:

```json
{"status":"ok","component":"backend","dataset_version":"sha256-09fc6649582f","embedding_model":"all-MiniLM-L6-v2 (onnx)","courses":36,"chunks":46}
```

Search latency in the container was about 40–200 ms per query. The API log records `query_chars=58 top_k=3 results=['STAT 220', 'STAT 120', 'STAT 111'] latency_ms=206`; query text is not logged.

## Frontend → backend integration

Checked on 2026-10-14 from a clean worktree of the pushed branch (`66e6964`, which contains the latest `main`, `ee6a04b`). John's CSV came from PR #2 commit `7b75ade`; his fork has since been deleted, so that is the newest available copy. Its SHA-256 matches the dataset version above.

- **Containers:** Akshaya's frontend image and the backend image ran on one Docker network, with `SEARCH_API_URL=http://backend:8000/search`, the service-name wiring the team-wide compose will need. Both `/health` endpoints reported OK, and the backend served 36 courses and 46 chunks.
- **Real UI in headless Chrome:** the form was filled and submitted in live mode, not the synthetic preview. Two searches, "Bayesian statistics" (PhD / research) and "deep learning for NLP" (Tech / ML, with completed courses), each rendered "5 courses returned", the dataset version `sha256-09fc6649582f`, five cards with context and retrieval date, and 20 source links. Both `POST /search` calls returned 200, with 0 JavaScript errors. Screenshot: [live-search-bayesian.png](screenshots/live-search-bayesian.png).
- **The frontend's own code:** `buildRequest` and `normalizeResponse` from `frontend/static/api.mjs` ran against the live proxy for four profiles. All responses validated. The proxy rejected a blank query and `top_k: 50` with 400 before reaching the backend.
- **Display observations, for the frontend owner:** for short descriptions, the "Supporting context" box repeats most of the description. The description text still includes the raw `Course site: https://…` line, which is also listed as a source.

## Example queries

`score` is the cosine similarity of the course's best chunk. These are smoke queries chosen by the backend owner to exercise the pipeline. **They are not Ming's acceptance queries**, which are still pending (see below).

| Query | Top results (score) | Assessment |
| --- | --- | --- |
| `Bayesian statistics` | STAT 120 (0.72), STAT 220 (0.66), STAT 111 (0.57), STAT 131, STAT 244 | Correct: both Bayesian courses first |
| `interpretable machine learning and causal inference` | COMPSCI 2823R (0.49), STAT 111 (0.46), APCOMP 221 (0.42), COMPSCI 1810, STAT 220 | Reasonable; no dedicated causal-inference course in the data |
| `deep learning for NLP` | COMPSCI 1870 (0.36), APMTH 226 (0.34), COMPSCI 2821R (0.29), APCOMP 209B, COMPSCI 1090B | Correct top result |
| `capstone project with an industry partner` | APCOMP 297R (0.53), then all others < 0.17 | Correct, with a clear margin |
| `how do computer networks and distributed systems scale` | COMPSCI 1450 (0.51), COMPSCI 2050 (0.27), COMPSCI 1200, COMPSCI 1650 | Correct top result |
| `statistics elective` | STAT 220 (0.57), STAT 120 (0.54), STAT 111, STAT 230, STAT 149 | Requirement-area header works |
| `asdkjh qwpoeiru zzxx` (direct API call) | `[]` (best 0.15, below the 0.25 threshold) | Correct empty result, **but only for raw queries**; see failure 6 |
| Frontend profile: `Interests: deep learning for NLP` / `Career goal: PhD / research` / `Background: Statistics and Python` / `Completed courses: APCOMP 209A, COMPSCI 1810` | COMPSCI 1870 (0.49), APCOMP 209B (0.47), COMPSCI 1090B (0.46), APCOMP 215 (0.44), APCOMP 209A (0.38) | Right top result; see failures 1–3 |
| `quantitative finance, stochastic processes, portfolio optimization` | STAT 131 (0.41), COMPSCI 1840 (0.41), COMPSCI 1820 (0.34), … | Data gap; see failure 4 |

## Observed failures

1. **Profile labels compress scores.** The frontend's labeled query format raises every score to roughly 0.45–0.55. The query `Interests: interpretable machine learning` / `Career goal: PhD / research` / `Background: Statistics and Python` / `Completed courses: APCOMP 209A` returned five courses between 0.51 and 0.54. The ranking is still usable, but the threshold and score gaps carry less information. Planned fix: the MS3 LLM interpretation step rewrites the profile into a retrieval query.
2. **Completed courses are returned.** APCOMP 209A appears for a student who has completed it. The API contract deliberately leaves completed courses as query text, not a filter. Filtering belongs to the MS3 planner and validator.
3. **Cross-listed duplicates.** APCOMP 209B and COMPSCI 1090B (Data Science 2) are one course under two codes and both appear. This needs a cross-listing key from ingestion (John), or merging on the "also offered as" notes.
4. **No finance coverage.** The 36-course dataset has no finance or economics courses, so the quant-finance track query returns loosely related time-series and RL courses. This is a data scope gap, not a retrieval bug, and the quant-finance acceptance query is expected to fail until the dataset expands.
5. **Abandoned chunking design (fixed).** The first index also embedded catalog notes and a requirements/instructor chunk per course (108 chunks). Those short chunks behaved like title matches, so `Bayesian statistics` returned "Counts toward… Instructors: …" as context instead of the description. The design was changed to embed descriptions only (46 chunks); see [backend/README.md](../../backend/README.md#design-decisions).

6. **The empty state is unreachable from the real frontend.** The frontend wraps every search in labels, and the label text alone matches ML courses. Measured through the frontend proxy:

   | Interests | Career goal | Top scores |
   | --- | --- | --- |
   | `asdkjh qwpoeiru zzxx` | Tech / ML | 0.36 0.28 0.28 0.27 0.26 |
   | `xyz` | Tech / ML | 0.37 0.32 0.31 0.29 0.29 |
   | `deep learning for NLP` | Quant finance | 0.35 0.34 0.34 0.32 0.30 |

   Nonsense scores (up to 0.37) overlap with real but weak matches (0.30–0.35), so no single threshold separates them, and the threshold was left at 0.25. Fixing this means changing how the profile is turned into a query: for example, the backend embeds the `Interests` line separately and applies the threshold to it, or the MS3 LLM rewrites the profile. Either changes the agreed contract, so it needs a team decision.

## Acceptance queries: pending

Ming's five acceptance queries, with expected courses, are not yet available. When they are, save them in the format documented in [evaluate.py](../../backend/wayfind_retrieval/evaluate.py) and run:

```sh
cd backend && uv run python -m wayfind_retrieval.evaluate <queries.json> --k 5 --out ../docs/ms2/retrieval-logs/acceptance-report.json
```

The report gives hit@5, MRR, and NDCG@5 per query and on average, plus any expected course IDs missing from the dataset. This becomes the embedding-similarity baseline that the MS3 trained ranker must beat.
