# MS2 local Docker integration

This file records one **locally executed** test. It is not an independent peer
clean-checkout or the final milestone submission.

## Verified run

| Property | Observed value |
| --- | --- |
| Date / time | 2026-10-14T16:10:37-04:00 |
| Verifier | Tavish (local Mac) |
| Git branch | `tavish/ms2-integration` |
| Base commit SHA | `daadcb9fdc52acee1a4f13345975656e6276b90c` (may include uncommitted changes; **not** the final PR SHA) |
| Start command | `docker compose up -d --build` from repository root |
| Docker Engine / Compose | `29.8.0` / `5.5.1` |
| Data source | `data/scraped_sheet1.csv` (37 rows; source dates: 2026-10-08) |
| Data SHA-256 | `09fc6649582ff140cab0e50a7fdfe555cf80c2b1d4de7758ad94b1e8e8d20b88` |
| Backend dataset version | `sha256-09fc6649582f` |
| Retrieval model | `all-MiniLM-L6-v2 (onnx)` |
| Index | 36 courses, 46 chunks |
| Live-query result count | 5 courses, source links present |

The backend and frontend `/health` endpoints responded successfully, and the
frontend's `/search` proxy returned live results carrying the same dataset version
as the backend. The frontend's own health check only establishes that its server
is alive, so the separate `/search` test is necessary.

## Smoke-test input and observed output

```text
Interests: Bayesian statistics
Career goal: PhD / research
```

- `STAT 120` — Introduction to Bayesian Inference and Applications
- `STAT 220` — Bayesian Inference
- `STAT 111` — Introduction to Statistical Inference
- `APCOMP 209A` — Data Science 1: Introduction to Data Science
- `APCOMP 209B` — Data Science 2: Advanced Topics in Data Science

These are smoke-test observations, **not Ming's five acceptance examples** and not
evidence that the recommendations satisfy academic degree requirements.

## Saved files from this run

- [Run metadata](integration-runs/run-20261014-161037/run-info.json)
- [Backend health](integration-runs/run-20261014-161037/backend-health.json)
- [Frontend health](integration-runs/run-20261014-161037/frontend-health.json)
- [Full search response](integration-runs/run-20261014-161037/live-search.json)
- [Compose service status](integration-runs/run-20261014-161037/compose-status.txt)
- [Docker logs](integration-runs/run-20261014-161037/docker-compose.log)

## Screenshots and remaining verification

- [ ] Save `docs/ms2/screenshots/integration-live-search.png` showing the **live**, non-synthetic website results and dataset metadata.
- [ ] Save `docs/ms2/screenshots/integration-containers.png` showing the Docker containers running.
- [ ] Have a second team member clone the merged revision and execute the root Compose command independently; record their result.
- [ ] Replace the base SHA above with the final verified commit SHA after the code is committed and reviewed.
- [ ] Run Ming's five agreed acceptance queries separately; do not substitute this smoke test for them.
- [ ] Review the logs before committing, to ensure no passwords, tokens, private student profiles, or other secrets are included.

**Scope:** The Compose workflow indexes the committed course CSV and runs retrieval.
It does not rerun John's original scraper, perform degree-rule planning, or deploy
an internet-accessible backend.
