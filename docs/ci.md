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

Creating the workflow displays pass/fail checks; it does not itself block merging. The versioned [required-checks ruleset](../.github/rulesets/required-pr-checks.json) defines the repository's intended merge policy. **The JSON is a configuration template, not an active GitHub setting.** The current collaborator account has push access but not admin access; no ruleset has been activated by this change.

The prepared ruleset requires pull requests and all three checks from the GitHub Actions app before merging into the default branch (`main`) or any `milestone*` branch. The PR must be tested against the latest target-branch code. There are no configured bypass actors. Feature branches remain writable so contributors can push code for CI to test. The policy applies to every contributor, not only Akshaya; the tests currently cover the frontend component.

One-time setup by the repository owner/admin:

1. Review and merge the workflow and its test implementation in PR #8 into `main`, then update any existing milestone branches to include it.
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
