# WayFind — AC215 Project Plan

## Tasks and responsibilities

Proposed roles; names are to be assigned. Team capacity: five members, 3–4 hours per person per week. Outputs below are planned deliverables, not completion claims.

### Member A — Requirements, planning, and validation

- Define the project scope, degree-rule specification, and acceptance examples.
- Implement the constraint planner and independent validation checks after MS2, with API integration support from C.
- Define and test locked-course and minimal-change replanning behavior.
- Maintain acceptance criteria and evaluate whether outputs satisfy the intended user workflow.

**Expected outputs:** Scope and rule specification, five initial test queries, planner and validator, rule and replanning tests.

### Member B — Data and source verification

- Collect an initial 10-course sample, then expand to approximately 30–50 curated courses.
- Build ingestion, cleaning, deduplication, and versioned snapshots.
- Preserve course identifiers, descriptions, terms, source URLs, and uncertainty flags.
- Coordinate relevance labels and a small, manually verified faculty/publication dataset for later milestones.

**Expected outputs:** Reproducible data pipeline, documented schema, versioned course and label datasets, source-backed faculty records.

### Member C — Retrieval, modeling, and API

- Implement chunking, embeddings, vector database integration, and the retrieval API.
- Train a lightweight course ranker and compare it with an embedding baseline.
- Track experiments and integrate A's planner and validator into the backend API.
- Implement evaluation metrics and model-release checks with D.

**Expected outputs:** Retrieval service, trained ranker, baseline comparison, documented planning API, evaluation reports.

### Member D — Infrastructure and integration

- Set up dependency management, Dockerfiles, and the single-command development pipeline.
- Coordinate Vertex AI training and pipelines, Cloud Run deployment, and logging.
- Implement GitHub Actions, Kubernetes deployment, and automated retraining/deployment orchestration.
- Verify reproducibility, deployment configuration, and scaling behavior.

**Expected outputs:** Containerized workflow, cloud training/pipeline configurations, deployed services, CI/CD workflows, deployment evidence.

### Member E — Frontend and user experience

- Build the input form and retrieval results page from the proposal mockup.
- Connect the interface to the API and add roadmap, source-detail, and replanning views.
- Implement loading, error, empty-result, and conditional-plan states.
- Coordinate user-flow testing and assemble demo materials supplied by the team.

**Expected outputs:** Working frontend, end-to-end user flow, usability feedback, demo screenshots and video assembly.

**Shared tasks:** Each member writes their component's tests and documentation and contributes presentation material. Another member verifies each deliverable. All members must understand the complete system; integration and final documentation are not assigned to one person alone.

## Milestone timeline and expected outputs

All deadlines below are in 2026, at **10:00 PM Eastern Time**. Dates and requirements follow the [official course milestones](https://harvard-iacs.github.io/2026-AC215/projects/). Product scope reductions remain proposals to align with the TF.

### MS1 — Proposal | September 29

**Tasks:** Define the user problem, stakeholders, data sources, success criteria, initial architecture, and application mockup.

**Ownership:** A leads proposal coordination; all members contribute and review.

**Expected outputs:** Written proposal and user-flow mockup. The local proposal uses the name Waypoint; this repository is named WayFind.

### MS2 — Data pipeline and application skeleton | October 20

**Tasks:**

- A: Finalize scope, rule terminology, and five retrieval acceptance examples.
- B: Deliver the initial course dataset, preprocessing scripts, and snapshot/version records.
- C: Implement chunking, embeddings, vector database integration, and query-to-context retrieval.
- D: Package the components with Docker, `uv`/`pyproject.toml`, configuration examples, and a single-command pipeline.
- E: Connect the input form to the retrieval API and display results with sources.

**Expected outputs:** Reproducible environment, versioned dataset, containerized retrieval pipeline, working app skeleton, setup instructions, environment screenshots, and sample input/output logs. Full roadmap generation, trained ranking, and mentor recommendations are deferred beyond MS2.

**Internal timeline:** October 12 — sample data and API contract; October 15 — integrated retrieval demo; October 18 — feature freeze and clean-checkout verification; October 19 — final checks and slides.

**Submission:** `milestone2` branch and full commit hash on Canvas; slides for the TF evaluation. [MS2 requirements](https://harvard-iacs.github.io/2026-AC215/milestone2/)

### MS3 — Model and backend integration | November 12

**Tasks:**

- A/B: Encode and audit the supported degree rules; build a baseline planner and independent validator.
- B/C: Prepare relevance labels, train the course ranker, and compare it against the baseline.
- C/D: Record experiments, complete a reproducible Vertex AI training run, and automate preprocessing/training/evaluation with a pipeline.
- C/D/E: Deploy the backend on Cloud Run, add logging, and verify API access and responses.

**Expected outputs:** Tracked training run, model and evaluation artifacts, automated ML pipeline, working planning API, serverless deployment, monitoring logs, API tests, and reproducibility instructions. Unknown future offerings remain conditional rather than verified.

**Internal timeline:** November 1 — initial training and baseline comparison; November 8 — cloud API and pipeline working; November 11 — evidence and integration checks complete.

**Submission:** `milestone3` branch and full commit hash on Canvas; slides and running-system evidence. [MS3 requirements](https://harvard-iacs.github.io/2026-AC215/milestone3/)

### MS4 — Complete user workflow and CI | December 1

**Tasks:**

- A/C: Implement locked-course and minimal-change replanning with validation.
- B/E: Add a small set of source-backed faculty cards and verify displayed evidence.
- E/C: Complete the roadmap interface, API integration, and visible failure/uncertainty states.
- All members: Document architecture and add unit, integration, and end-to-end tests; D coordinates CI.

**Expected outputs:** Application design document, functioning local end-to-end application, containerized frontend, GitHub Actions CI, test documentation, and at least **50% API/backend code coverage**.

**Internal timeline:** November 22 — complete primary user flow and an early Kubernetes smoke deployment; November 29 — freeze features and complete MS4 evidence. The early cluster check is an internal risk-reduction target for MS5.

**Submission:** `milestone4` branch and full commit hash on Canvas; slides and frontend/API demo evidence. [MS4 requirements](https://harvard-iacs.github.io/2026-AC215/milestone4/)

### MS5 — Deployment and final delivery | December 11

**Tasks:**

- D, supported by component owners: Complete Kubernetes deployment and demonstrate scaling.
- C/D: Trigger retraining on data or code updates and deploy models only after documented validation checks pass.
- All members: Reach at least 70% API/backend line coverage, verify CI/CD, and finalize documentation.
- E coordinates the demo; all members contribute to the video, blog, and final presentation.

**Expected outputs:** Publicly accessible cloud application, Kubernetes scaling evidence, deploy-on-merge CI/CD, gated retraining/deployment workflow, at least **70% API/backend line coverage**, final README, a **6-minute MP4 video (at least 720p)**, a **600–800-word Medium post**, and self/peer evaluations.

**Internal timeline:** December 6 — engineering checks complete; December 7 — release freeze; December 9 — demo rehearsal; **December 10 — live showcase**; December 11 — final submission.

**Submission:** `main` branch/repository link, video, blog link, and self/peer reviews through the course portal. No late submissions. [MS5 requirements](https://harvard-iacs.github.io/2026-AC215/milestone5/)
