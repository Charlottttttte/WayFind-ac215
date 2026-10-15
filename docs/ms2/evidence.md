# MS2 evidence index

This index retains the team’s recorded integration evidence. The earlier coordination checklist, demo runbook, and slide outline have been removed. Recorded runs are historical evidence, not a fresh verification of the current checkout.

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

## Recorded artifacts

- [Container integration report](integration-report.md): commands, environment, observations, and limitations.
- [Retrieval evidence](retrieval-evidence.md): the backend retrieval example and its recorded outputs.
- [Integration logs and sample response](integration-runs/run-20261014-161037/): artifacts from the recorded local run.
- [Acceptance-query inputs](acceptance-queries.json): the team’s five cases; their presence does not establish that they passed.
- [Earlier frontend observations](../../frontend/VERIFICATION.md): synthetic interface and component-container checks.

Retain the exact command, commit, dataset version, logs, and sample input/output for each new run. The frontend health endpoint alone does not establish retrieval availability.
