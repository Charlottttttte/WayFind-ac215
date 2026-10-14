# MS2 demo runbook

Coordinator: Akshaya. Target rehearsal: October 19, 2026.

Status: **starter runbook; integrated retrieval evidence and team contributions are pending**. Frontend implementation is proposed in [PR #8](https://github.com/Charlottttttte/WayFind-ac215/pull/8). Demo coordination is tracked in [issue #7](https://github.com/Charlottttttte/WayFind-ac215/issues/7).

## Before rehearsal

- [ ] Ming supplies the agreed MS2 scope and five acceptance examples.
- [ ] John supplies the versioned dataset, source provenance, and missing-field caveats.
- [ ] Shravya confirms the frontend contract and a working retrieval service.
- [ ] Tavish supplies the full pipeline's one-command startup and environment evidence.
- [ ] Akshaya connects the actual API, captures the frontend flow, and assembles contributed slides.
- [ ] Another member reproduces the integrated run from a clean checkout.
- [ ] Record the tested commit, dataset version, exact command, and environment in [evidence.md](evidence.md).

## Live demonstration

1. Show the pinned commit and dataset version. Use Tavish's verified startup command; do not substitute a frontend-only command as evidence of the whole pipeline.
2. Open the frontend with synthetic preview **off**. Enter one of Ming's agreed profiles and explain the interests/career goal.
3. Submit the query. Show the loading state and returned course cards.
4. Open one source and compare the supporting passage with the returned context. Identify course IDs, terms, retrieval dates, and unresolved fields.
5. Show the matching input/output artifact and retrieval log. Explain collection → chunking → embeddings → vector DB → retrieved context → UI.
6. Summarize outcomes for all five acceptance examples, including misses and failures. Do not describe sample fixtures as retrieval results.
7. Separately demonstrate empty and error states using labeled synthetic preview if needed. Explain that these are interface checks.
8. State limits: this slice retrieves courses; it does not validate a degree plan, enforce prerequisites, generate a three-semester roadmap, or find mentors.

If retrieval fails during rehearsal, record the failure and use a **previously verified** recording with its commit/dataset identifiers if available. If none exists, show the labeled interface preview and report the integration gap explicitly.

## Presentation sequence (15 minutes)

| Segment | Time | Contributor |
| --- | --- | --- |
| User problem, MS2 scope and acceptance examples | 2 min | Ming |
| Dataset, provenance, cleaning and snapshot | 3 min | John |
| Retrieval design and one query-to-context example | 3 min | Shravya |
| Environment, containers and reproducibility | 2 min | Tavish |
| Frontend flow, evidence and observed limitations | 3 min | Akshaya |
| Remaining gaps and next technical decisions | 2 min | Team |

These are proposed allocations for the team-led presentation. Keep Q&A separate. Each owner contributes slides and documentation for their component, and every member prepares to explain the complete system. Use [slides-outline.md](slides-outline.md) as the collection checklist.

## Submission handoff

- [ ] Team integration owner assembles the final `milestone2` branch.
- [ ] Re-run the documented full workflow from that exact commit.
- [ ] Update evidence and slides to match the final commit, with no unsupported completion claims.
- [ ] Capture the full 40-character commit SHA for submission on Canvas by **October 20, 2026, 10:00 PM ET**.
- [ ] Confirm the team has submitted the hash and prepared slides for the TF meeting.

Source: [official MS2 requirements](https://harvard-iacs.github.io/2026-AC215/milestone2/). This runbook does not submit anything to Canvas or merge branches.
