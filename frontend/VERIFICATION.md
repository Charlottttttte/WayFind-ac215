# Frontend verification - October 13, 2026

## Vercel follow-up

Hosted frontend: https://wayfind-ac215.vercel.app. Deployment ID: `dpl_83QamqhMJkhM4nrV2Fc5EX6zwjQa`.

- Increased form and supporting-text sizes, added an explicit sample-search entry point, and scroll to results after successful mobile search.
- Vercel's Python 3.12 build completed successfully; static homepage, stylesheet, and JavaScript returned HTTP 200 without authentication.
- Hosted synthetic search returned two labeled fixture cards. Switching back to live search displayed the explicit backend-not-connected message.
- Hosted `POST /search` returned HTTP 503 with `SEARCH_NOT_CONFIGURED`, as expected without `SEARCH_API_URL`.
- The project is in the `portfolio-website12` Vercel workspace. GitHub auto-deploy connection was unsuccessful; this deployment used the CLI. A future push alone will not update the site until Git integration is connected.
- Backend hosting and real retrieval remain pending. The public site is a working interface preview, not a completed RAG deployment.

This document records historical frontend observations from October 13. For the team’s later local backend/frontend run, see [the integration report](../docs/ms2/integration-report.md).

Scope: local MS2 frontend and proxy. Base: `6dab78dfe754a9d8cb91aa912a92a40b7c9c4b5f` on `main`.

## Observed checks

| Check | Result |
| --- | --- |
| `docker build -t wayfind-frontend:ms2 frontend` | Passed on local Docker Desktop. |
| `FRONTEND_PORT=8081 docker compose -p wayfind-ms2-frontend -f frontend/compose.yaml up --build -d --wait` | Passed; service reached healthy state. Port 8081 avoided the separate Python preview on 8080. |
| `GET http://127.0.0.1:8081/health` | HTTP 200, `{"status":"ok","component":"frontend"}`. |
| Container `POST /search` while no retrieval service runs | HTTP 503, `{"error":"Search service unavailable"}`. No mock fallback. |
| Browser synthetic success, empty, error and retry | Observed two labeled sample cards; no-match guidance; simulated error; successful retry with profile values retained. |
| Browser live mode while no retrieval service runs | HTTP 503 message displayed and submit button re-enabled. |
| Browser loading | Visible status and disabled submit button observed during synthetic delay. |
| Responsive layout | Checked at 1280px and 390px; document width equaled viewport width at each size. |

Docker Desktop was started before container verification.

## Screenshots

These are viewport captures of **synthetic UI preview**, not real course data or proof of end-to-end retrieval. The entered profile is a test example.

![Desktop synthetic preview](screenshots/desktop-synthetic.png)

![Mobile profile view](screenshots/mobile-synthetic.png)

## Scope of these observations

The screenshots above show synthetic frontend behavior. The [integration report](../docs/ms2/integration-report.md) and [retrieval evidence](../docs/ms2/retrieval-evidence.md) contain the team’s later real-data observations and remaining verification limits.
