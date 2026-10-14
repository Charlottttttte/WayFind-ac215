# MS2 evidence register

Keep evidence tied to the exact run, not only to the presence of source code. This is a starter register; pending entries are not completed deliverables.

## Integrated run identity

| Field | Value |
| --- | --- |
| Run date and verifier | 2026-10-14T16:10:37-04:00 — Tavish local run; peer pending |
| Full commit SHA / branch | `daadcb9fdc52acee1a4f13345975656e6276b90c` on `tavish/ms2-integration` — base SHA only; working tree/final milestone commit pending |
| Environment and running-instance screenshot | Pending |
| Full pipeline command | `docker compose up -d --build` from repository root; [local run evidence](integration-report.md) |
| Dataset version / source dates | Pending John |
| Retrieval model/version and index snapshot | Local `/health`: `all-MiniLM-L6-v2 (onnx)`, dataset `sha256-09fc6649582f`; [run evidence](integration-report.md) (owner sign-off pending) |
| Input profile/query | Pending Ming's agreed example |
| Input/output artifact and logs | [Real local search + logs](integration-runs/run-20261014-161037/live-search.json) and [integration summary](integration-report.md); five acceptance queries pending |
| Peer clean-checkout verification | Pending |

## Evidence by component

| Owner | Required material | Current status |
| --- | --- | --- |
| Ming | Scope, terminology, five acceptance examples with expected courses/evidence | Pending team contribution |
| John | Dataset snapshot, cleaning command, source URLs/dates, access conditions, uncertain fields | Pending team contribution |
| Shravya | Chunking/embedding/index commands; retrieved context and sources; API examples and failures | Pending team contribution |
| Tavish | Full Compose/startup instructions, component versions, running-instance screenshot, pipeline logs | [Local integration evidence](integration-report.md) captured; screenshots, peer verification and final commit pending |
| Akshaya | Frontend profile/results screenshots and loading/empty/error behavior | [PR #8](https://github.com/Charlottttttte/WayFind-ac215/pull/8) contains local synthetic screenshots and component verification; real retrieval screenshots remain pending |
| Second verifier | Clean-checkout run of the full pipeline | Pending |

## Acceptance-query results

Ming supplies the exact inputs and expected evidence. Shravya records retrieval behavior; Akshaya records the UI behavior. Do not fill expected course IDs by guessing.

| Example | Input and expected evidence | Actual retrieved courses/context | Result and failure notes | Artifact |
| --- | --- | --- | --- | --- |
| 1 | Pending | Not run | Pending | Pending |
| 2 | Pending | Not run | Pending | Pending |
| 3 | Pending | Not run | Pending | Pending |
| 4 | Pending | Not run | Pending | Pending |
| 5 | Pending | Not run | Pending | Pending |

## Evidence handling

Record a relative artifact path or stable link, command, exit status, commit SHA, and dataset version for every run. Keep raw logs plus a small input/output artifact. Label fixture/stub tests as simulated. Redact credentials and private student details before committing evidence. Do not claim that the frontend health endpoint proves retrieval is available.

Known boundary: the frontend PR has a proposed API contract, 11 passing local automated checks, browser state checks, and a successful component container build/start. Those results do not demonstrate the team ingestion/indexing/retrieval pipeline or peer reproduction.

See also [Tavish's locally verified Compose run](integration-report.md) (screenshots and peer confirmation still pending).
