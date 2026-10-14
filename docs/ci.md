# Pull-request checks

The [PR checks workflow](../.github/workflows/pr-checks.yml) runs on every opened, updated, reopened, or ready-for-review pull request, including drafts. It also checks pushes to `main` and `milestone2`. Once merged into the default branch, it can be started from the Actions tab with **Run workflow**.

| Check | What it verifies |
| --- | --- |
| JavaScript tests | Query construction, response validation, source URLs, timeout/error handling, and the hosted missing-backend message. Uses Node.js 24 and the built-in test runner. |
| Python and API tests | Asset access, request validation, proxy forwarding, upstream errors, and the Vercel handler. Uses Python 3.12 and temporary local HTTP servers. |
| Docker build and smoke test | Dockerfile and frozen uv dependencies build; the container serves health/static endpoints; an unavailable backend returns an explicit error. |

Open a PR's **Checks** tab for the result and logs of each job. Push a fix to the same branch to rerun the checks. New runs cancel outdated ones for the same PR. No live retrieval service, Vercel login, API key, or repository secret is needed. The workflow has read-only repository permissions and does not deploy or merge code.

Run the test suites locally from the repository root:

```sh
node --test frontend/tests/api.test.mjs
python3 -m unittest discover -s frontend/tests -v
docker build --tag wayfind-frontend:ci frontend
```

Current coverage is the frontend and its proxy/adapter. It does not establish retrieval relevance, production readiness, or an end-to-end run with real course data. Backend/ingestion owners can extend this workflow when their tests land. See [frontend verification](../frontend/VERIFICATION.md) for those evidence boundaries.

## Requiring checks before merge

Creating the workflow displays pass/fail checks; it does not itself block merging. A repository admin can select the three job names above as required status checks in a branch ruleset for `main` and `milestone2`, after they have run. The current collaborator account has push access but not admin access, so this change does not modify branch rules or merge any PR.

For PRs that do not yet include the workflow, it becomes available after this change is merged into their base branch. Avoid path-based workflow exclusions if these checks become mandatory, since excluded workflows can leave required checks pending.
