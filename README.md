# WayFind — AC215 Project

A course-and-mentor roadmap project for Harvard SEAS Data Science master's students, introduced as **Waypoint** in the MS1 proposal.

The long-term goal is to combine source-grounded recommendations, explicit degree-rule checks, and adaptive course planning. Any validity claim will be limited to the audited rules and data available to the system; future offerings and unresolved requirements must remain explicitly conditional.

**Current status:** Planning documentation only. The application, data pipeline, and deployment described below are planned deliverables, not completed features. Runnable setup instructions will be added with the implementation.

## MS2 kickoff meeting

- **Target meeting date:** October 9, 2026; exact time to be agreed by the team.
- **Duration:** 30 minutes.
- **Team capacity:** Five members, approximately 3–4 hours per person per week.
- **MS2 deadline:** October 20, 2026, at 10:00 PM Eastern Time.
- **Planning status:** Scope and role assignments below are proposals for discussion, not confirmed assignments or TF-approved changes to the final project scope.

### Objective

Agree on a realistic MS2 scope, assign clear ownership, and establish integration deadlines. Each member should leave with a concrete deliverable, dependencies, and acceptance criteria.

### Proposed MS2 user flow

> A user enters their background and interests. The application retrieves relevant courses from a versioned dataset and displays matching courses, supporting context, and source references.

The proposed initial scope is one degree program, one primary interest direction, and approximately 30–50 curated courses. The course count is a team planning target, not a course requirement.

The trained ranker, constraint solver, full three-semester roadmap, mentor recommendation workflow, and adaptive replanning are deferred beyond MS2. This sequencing does not by itself remove them from the final project. Any roadmap placeholders must be labeled as illustrative; retrieval results must not be presented as a verified graduation plan.

### Agenda

1. **Current status and availability — 5 minutes**
   - Confirm each member's available work periods, relevant experience, and existing work.
   - Check GitHub and course-data access; check GCP access early for later milestones.
   - Record access blockers and who will resolve them. Local execution is sufficient for the MS2 environment evidence.

2. **Confirm MS2 scope — 5 minutes**
   - Agree on the target user, initial course subset, and minimum user flow.
   - Identify deferred features and any proposed scope changes to discuss with the TF.

3. **Agree on data and interfaces — 7 minutes**
   - Decide the course schema, snapshot location, and data-versioning approach.
   - Agree on the retrieval API request and response fields.
   - Establish a small shared sample so frontend, retrieval, and container work can proceed in parallel.

4. **Assign responsibilities — 8 minutes**
   - Assign one named owner to each workstream below.
   - Confirm deadlines, dependencies, and who will verify each deliverable.

5. **Set checkpoints — 5 minutes**
   - Schedule the first integrated demo and feature freeze.
   - Choose the submission owner and reviewer.

## Proposed task allocation

Roles A–E are placeholders to be assigned during the meeting. Each member owns the documentation and basic verification for their component. Work should fit the stated weekly capacity; optional features yield to integration and reproducibility.

### Member A — Scope, requirements, and acceptance criteria

Suggested for the member who led brainstorming and proposal writing, subject to team agreement.

- Write a one-page MS2 scope statement.
- Clarify degree-rule terminology and its implications for the data schema, checking the applicable cohort and official sources rather than treating proposal prose as an executable specification.
- Prepare five representative queries with expected relevant courses or supporting evidence. These are smoke-test examples, not a full recommendation benchmark.
- Review whether the integrated application addresses the intended user need.
- Provide the problem statement and scope slides.

**Deliverable:** Agreed scope, documented requirements, and five acceptance examples.

**Boundary:** This role does not include writing everyone's documentation or taking over unfinished integration work.

### Member B — Data collection and preprocessing

- Deliver an initial sample of 10 real courses, then expand to approximately 30–50.
- Implement ingestion, cleaning, and deduplication.
- Preserve course identifiers, descriptions, terms, source URLs, retrieval dates, and missing or uncertain fields.
- Save raw and processed snapshots and record their versions.
- Document access requirements and permitted use. If API access blocks progress, propose an appropriately sourced public-data subset rather than waiting for a full catalog.

**Deliverable:** A reproducible preprocessing command and versioned dataset with traceable sources.

**Dependency:** Agree on fields with A and C before expanding the sample.

### Member C — Retrieval pipeline and backend API

- Implement chunking, embeddings, and vector database integration.
- Build a minimal proposed `/search` endpoint; finalize its contract with E.
- Return matching courses, retrieved context, and source references.
- Run the five acceptance queries and document failures.
- Add basic retrieval and API tests.

**Deliverable:** A working query-to-context retrieval flow accessible through the API.

**Dependency:** Start with B's 10-course sample; do not wait for the full dataset.

### Member D — Environment, containers, and integration

- Establish repository structure and dependency management.
- Coordinate Dockerfiles, `uv`/`pyproject.toml` configuration, and Docker Compose.
- Connect ingestion, indexing, backend, and frontend into a documented workflow.
- Provide configuration examples without credentials and exact startup instructions.
- Coordinate a clean-checkout run by another member and collect environment evidence and logs.

**Deliverable:** A reproducible, single-command pipeline with documented prerequisites and execution evidence.

**Boundary:** Component authors supply their dependencies and execution instructions; D coordinates integration rather than implementing every component.

### Member E — Frontend and demo coordination

- Reuse the proposal's onboarding and results-page design.
- Connect the input form to the retrieval API.
- Display course results and supporting sources.
- Implement loading, empty-result, and request-error states.
- Assemble application screenshots and slides contributed by the team.

**Deliverable:** A usable application skeleton showing a real frontend-to-backend interaction.

**Dependency:** Use the agreed response fixture while C implements the API, then replace the fixture with the live endpoint before the integration demo.

## Shared working agreements

- Deliver a small working sample before expanding functionality.
- Keep data fields and API responses consistent with the agreed contract; communicate changes before merging them.
- Document and test your own component, including how to run it.
- Have another member verify each deliverable. A successful run on the author's machine alone is insufficient.
- Report blockers early, with a proposed fallback.
- Keep credentials out of Git and redact sensitive information in screenshots and logs.
- All members must understand the complete system and be prepared to explain components they did not author.
- The submission owner verifies completeness and submits the agreed commit; they are not responsible for finishing everyone else's work.

## Checkpoints

- **October 9:** Confirm scope, role owners, access, and meeting decisions.
- **October 12:** Share the first 10 courses and finalize the schema and API contract.
- **October 15:** Demonstrate user input → retrieval → results with sources.
- **October 18:** Freeze MS2 features; verify containerized execution and data-version tracking from a clean checkout.
- **October 19:** Fix remaining issues, finalize evidence, and rehearse the presentation.
- **October 20:** Submit the full commit hash from the `milestone2` branch by 10:00 PM ET.

Dates before October 20 are proposed internal checkpoints. The submission branch must be created and verified before submission; this README does not indicate that it already exists.

## MS2 completion checklist

These unchecked items track planned work. Consult the official instructions for the authoritative requirements.

- [ ] Document the working environment and include a screenshot of a running local or cloud instance.
- [ ] Containerize the pipeline components and provide build and dependency instructions, including the required `uv`/`pyproject.toml` setup.
- [ ] Make the pipeline runnable with one documented command after prerequisites and configuration are in place.
- [ ] Record the data version used by each component.
- [ ] Demonstrate collection, chunking, vectorization, vector database integration, and one complete query-to-context retrieval example.
- [ ] Preserve pipeline logs and a small sample input/output artifact.
- [ ] Provide the mockup and a minimal working frontend/backend interaction.
- [ ] Document exact setup and execution steps and verify them with another member.
- [ ] Prepare slides for the 15-minute TF presentation and team-wide Q&A.
- [ ] Verify the `milestone2` branch and submit its full commit hash on Canvas.

## Decisions to record at the meeting

- Named owner and reviewer for each workstream.
- Confirmed MS2 scope and deferred features.
- Data source, schema, storage location, and versioning approach.
- API request/response contract.
- Integration-demo time on October 15.
- Submission owner and reviewer.

## Course references

- [AC215 course website](https://harvard-iacs.github.io/2026-AC215/)
- [Official Milestone 2 instructions](https://harvard-iacs.github.io/2026-AC215/milestone2/)

Deadline and MS2 requirements checked on October 9, 2026. Follow subsequent course-staff updates if requirements change.
