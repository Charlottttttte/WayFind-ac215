# WayFind — AC215

## Background

WayFind, introduced as **Waypoint** in our MS1 proposal, is a course-and-mentor roadmap project for Harvard SEAS Data Science master's students.

Students need to connect their academic background and career interests with course choices, degree requirements, and potential research mentors. Relevant information is spread across course catalogs, program requirements, faculty profiles, and publications. A useful recommendation must account for these sources and constraints, rather than simply return courses with similar descriptions.

Our primary users are Data Science master's students. Program advisors and faculty are secondary stakeholders: the project aims to support more informed advising conversations and research inquiries.

## Project task and proposed solution

Given a student's background, completed courses, interests, and career goal, the proposed system will generate a three-semester course-and-mentor roadmap and update it as the student's situation changes. The proposal considers three goal tracks: tech/ML, quantitative finance, and PhD/research.

The planned tasks are to:

1. **Build a versioned data pipeline:** Collect and normalize course information, degree rules, faculty profiles, and publication evidence.
2. **Retrieve and rank relevant options:** Use retrieval to identify candidates and evaluate a trained relevance ranker against an embedding-similarity baseline.
3. **Construct and validate course plans:** Apply encoded degree requirements, prerequisites, known term offerings, and known time constraints through a constraint solver and validation checks.
4. **Ground mentor suggestions in research:** Link faculty recommendations to verified author identities and real publications; do not infer whether a faculty member is accepting students.
5. **Support adaptive replanning:** Update the roadmap after feedback or changes in completed courses while minimizing unnecessary changes.

**Proposed workflow:** Student profile → interpretation of goals → candidate retrieval → relevance ranking → constraint solver and validator → roadmap with supporting sources → feedback and replanning.

The proposal assigns interpretation and explanation to an LLM, relevance scoring to a ranking model, and rule enforcement to the solver and validator. Validity is limited to the audited rules and available data: unknown future offerings, unresolved prerequisites, and approval-dependent requirements must remain explicitly conditional. The output supports advising; it does not constitute official degree approval.

**Planned data sources:** Harvard course information and SEAS degree requirements; public faculty profiles; OpenAlex publication records; O*NET career-skill information; team-collected relevance labels; and test student profiles. These are proposal-level sources, not a claim that all integrations are implemented or access conditions have been verified in this repository.

**Evaluation focus:** Plan validity, source and citation correctness, relevance against baselines, and replanning stability. The initial scope is one degree program and a desktop web application; job search, automated faculty outreach, and predictions about faculty availability are outside scope.

**MS2 implementation slice:** A user enters their background and interests; the application retrieves relevant courses from a versioned dataset and displays matching courses, supporting context, and sources. The initial target is 10 sample courses, expanding to approximately 30–50. Full planning, trained ranking, and mentor recommendations follow in later milestones. Outputs below are planned deliverables, not completion claims.

**Shared tasks:** Each member writes their component's tests and documentation and contributes presentation material. Another member verifies each deliverable. All members must understand the complete system; integration and final documentation are not assigned to one person alone.

## Milestone timeline and expected outputs

All deadlines below are in 2026, at **10:00 PM Eastern Time**. Dates and requirements follow the [official course milestones](https://harvard-iacs.github.io/2026-AC215/projects/). Product scope reductions remain proposals to align with the TF.

### MS1 — Proposal | September 29

**Tasks:** Define the user problem, stakeholders, data sources, success criteria, initial architecture, and application mockup.

**Proposal contribution:** Ming led brainstorming and wrote the main proposal content.

**Expected outputs:** Written proposal and user-flow mockup. The local proposal uses the name Waypoint; this repository is named WayFind.

### MS2 — Data pipeline and application skeleton | October 20

**Tasks:**

- Ming: Finalize scope, rule terminology, and five retrieval acceptance examples.
- John: Deliver the initial course dataset, preprocessing scripts, and snapshot/version records.
- Shravya: Implement chunking, embeddings, vector database integration, and query-to-context retrieval.
- Tavish: Package the components with Docker, `uv`/`pyproject.toml`, configuration examples, and a single-command pipeline.
- Akshaya: Connect the input form to the retrieval API and display results with sources.

**Expected outputs:** Reproducible environment, versioned dataset, containerized retrieval pipeline, working app skeleton, setup instructions, environment screenshots, and sample input/output logs. Full roadmap generation, trained ranking, and mentor recommendations are deferred beyond MS2.

**Internal timeline:** October 12 — sample data and API contract; October 15 — integrated retrieval demo; October 18 — feature freeze and clean-checkout verification; October 19 — final checks and slides.

**Submission:** `milestone2` branch and full commit hash on Canvas; slides for the TF evaluation. [MS2 requirements](https://harvard-iacs.github.io/2026-AC215/milestone2/)

### MS3 — Model and backend integration | November 12

**Tasks:**

- Encode and audit the supported degree rules; build a baseline planner and independent validator.
- Prepare relevance labels, train the course ranker, and compare it against the baseline.
- Record experiments, complete a reproducible Vertex AI training run, and automate preprocessing/training/evaluation with a pipeline.
- Deploy the backend on Cloud Run, add logging, and verify API access and responses.

**Expected outputs:** Tracked training run, model and evaluation artifacts, automated ML pipeline, working planning API, serverless deployment, monitoring logs, API tests, and reproducibility instructions. Unknown future offerings remain conditional rather than verified.

**Internal timeline:** November 1 — initial training and baseline comparison; November 8 — cloud API and pipeline working; November 11 — evidence and integration checks complete.

**Submission:** `milestone3` branch and full commit hash on Canvas; slides and running-system evidence. [MS3 requirements](https://harvard-iacs.github.io/2026-AC215/milestone3/)

### MS4 — Complete user workflow and CI | December 1

**Tasks:**

- Implement locked-course and minimal-change replanning with validation.
- Add a small set of source-backed faculty cards and verify displayed evidence.
- Complete the roadmap interface, API integration, and visible failure/uncertainty states.
- Document architecture, set up CI, and add unit, integration, and end-to-end tests.

**Expected outputs:** Application design document, functioning local end-to-end application, containerized frontend, GitHub Actions CI, test documentation, and at least **50% API/backend code coverage**.

**Internal timeline:** November 22 — complete primary user flow and an early Kubernetes smoke deployment; November 29 — freeze features and complete MS4 evidence. The early cluster check is an internal risk-reduction target for MS5.

**Submission:** `milestone4` branch and full commit hash on Canvas; slides and frontend/API demo evidence. [MS4 requirements](https://harvard-iacs.github.io/2026-AC215/milestone4/)

### MS5 — Deployment and final delivery | December 11

**Tasks:**

- Complete Kubernetes deployment and demonstrate scaling.
- Trigger retraining on data or code updates and deploy models only after documented validation checks pass.
- Reach at least 70% API/backend line coverage, verify CI/CD, and finalize documentation.
- Prepare the demo, video, blog, and final presentation.

**Expected outputs:** Publicly accessible cloud application, Kubernetes scaling evidence, deploy-on-merge CI/CD, gated retraining/deployment workflow, at least **70% API/backend line coverage**, final README, a **6-minute MP4 video (at least 720p)**, a **600–800-word Medium post**, and self/peer evaluations.

**Internal timeline:** December 6 — engineering checks complete; December 7 — release freeze; December 9 — demo rehearsal; **December 10 — live showcase**; December 11 — final submission.

**Submission:** `main` branch/repository link, video, blog link, and self/peer reviews through the course portal. No late submissions. [MS5 requirements](https://harvard-iacs.github.io/2026-AC215/milestone5/)
