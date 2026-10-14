# Pull-request checks

The [PR checks workflow](../.github/workflows/pr-checks.yml) runs on every opened, updated, reopened, or ready-for-review pull request, including drafts. It also checks pushes to `main` and `milestone*` branches. It can also be started from the Actions tab with **Run workflow**.

| Check | What it verifies |
| --- | --- |
| JavaScript tests | Query construction, response validation, source URLs, timeout/error handling, and the hosted missing-backend message. Uses Node.js 24 and the built-in test runner. |
| Python and API tests | Asset access, request validation, proxy forwarding, upstream errors, and the Vercel handler. Uses Python 3.12 and temporary local HTTP servers. |
| Docker build and smoke test | Dockerfile and frozen uv dependencies build; the container serves health/static endpoints; an unavailable backend returns an explicit error. |
| Backend retrieval tests | Data loading, chunking, index reuse/rebuild, best-chunk-per-course search, evaluation metrics, and the `/search` contract, with line coverage reported. Uses Python 3.12, uv, a synthetic fixture, and an offline test embedder. |
| Backend Docker build and retrieval smoke test | The backend image builds with the embedding model included; the indexer builds an index from the fixture with the real model; the API returns health, the expected top course, 422 for a blank query, and an empty result for nonsense. |

Open a PR's **Checks** tab for the result and logs of each job. Push a fix to the same branch to rerun the checks. New runs cancel outdated ones for the same PR. The checks need no live retrieval service, real course data, or secrets. The workflow has read-only repository permissions and never merges code. Production deployment is a separate dependent job, described below.

Run the test suites locally from the repository root:

```sh
node --test frontend/tests/api.test.mjs
python3 -m unittest discover -s frontend/tests -v
docker build --tag wayfind-frontend:ci frontend
(cd backend && uv run pytest --cov)
docker build --tag wayfind-backend:ci backend
```

The checks cover the frontend and its proxy/adapter, and the backend retrieval component. They use synthetic fixtures, so they do not establish retrieval relevance on real course data or an end-to-end run with the full team pipeline; see [retrieval evidence](ms2/retrieval-evidence.md). The ingestion owner can extend this workflow when those tests land. See [frontend verification](../frontend/VERIFICATION.md) for those evidence boundaries.

## Requiring checks before merge

Creating the workflow displays pass/fail checks; it does not itself block merging. The versioned [required-checks ruleset](../.github/rulesets/required-pr-checks.json) defines the repository's intended merge policy. **The JSON is a configuration template, not an active GitHub setting.** The current collaborator account has push access but not admin access; no ruleset has been activated by this change.

The prepared ruleset requires pull requests and all five checks from the GitHub Actions app before merging into the default branch (`main`) or any `milestone*` branch. The PR must be tested against the latest target-branch code. There are no configured bypass actors. Feature branches remain writable so contributors can push code for CI to test. The policy applies to every contributor, not only Akshaya; the tests currently cover the frontend and backend components.

One-time setup by the repository owner/admin:

1. PR #8 has been merged into `main`. Update any existing milestone branches to include the workflow and tests.
2. Open **Settings → Rules → Rulesets → New ruleset → Import a ruleset** and import `.github/rulesets/required-pr-checks.json`.
3. Confirm the target branches, check names, and **Active** enforcement, then save.
4. Confirm a PR to `main` shows the checks as required. A failed or pending check must prevent merging.

Alternatively, an administrator can apply the same file from the repository root:

```sh
gh api --method POST repos/Charlottttttte/WayFind-ac215/rulesets \
  --input .github/rulesets/required-pr-checks.json
```

Inspect existing rulesets before applying this command so it does not create duplicates. [GitHub's ruleset API](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset) requires repository Administration write permission. Required-check names and GitHub Actions app ID in the file were verified against a successful PR run.

For PRs that do not yet include the workflow, it becomes available after this change is merged into their base branch. Avoid path-based workflow exclusions if these checks become mandatory, since excluded workflows can leave required checks pending.

## Automatic production deployment

After a push to `main` (including a merged PR), the same workflow runs all five checks and then **Deploy production to Vercel**. The deployment job uses `needs` to depend on every check: a failure or cancellation prevents deployment. PR and milestone-branch runs never deploy and do not receive deployment credentials. A manual **Run workflow** on `main` reruns checks before deploying.

The job checks out the same commit that passed CI and uses Vercel CLI 64.0.1 from `frontend/`. Vercel builds the uploaded source once and publishes the existing project at <https://wayfind-ac215.vercel.app>. The workflow checks public assets and the API's method restriction after deployment and records the commit and deployment URL in the run summary. This smoke check does not establish live retrieval quality and does not automatically roll back a failed deployment.

Runs on `main` are serialized without cancelling an in-progress deployment. Before publishing, the job checks that its commit is still the latest `main`; superseded runs skip deployment. Keep Vercel's independent Git auto-deployment disconnected so it cannot publish before these CI checks pass.

Required repository **Actions secrets**:

| Name | Value source |
| --- | --- |
| `VERCEL_TOKEN` | Dedicated Vercel deployment token for the WayFind project/workspace. |
| `VERCEL_ORG_ID` | `orgId` in the locally linked `frontend/.vercel/project.json`. |
| `VERCEL_PROJECT_ID` | `projectId` in that same file. |

Create a dedicated token through Vercel account settings and store it in GitHub **Settings → Secrets and variables → Actions**. Never commit it or paste it into issues. Missing secrets fail the deployment job with an explicit configuration error; they do not silently report deployment success. Rotate the token before its expiry. See [Vercel CLI authentication](https://vercel.com/docs/cli) for noninteractive token usage.

After configuration, verify a `main` run shows all six jobs successful and the public site is reachable. Changes to CI must preserve the five required check names. When ingestion tests are available, add jobs for them and include them in the deployment job's `needs` and required-check ruleset.
