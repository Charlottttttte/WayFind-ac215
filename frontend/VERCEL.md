# Vercel deployment

Deploy **frontend/** as the project root, with Framework Preset **Other** and Output Directory **static**. `vercel.json` serves the static interface and maps `/search` to `api/search.py`, a serverless adapter around the same proxy used locally. Vercel does not run the Docker container or the long-lived local Python server.

The sample-search button works without a backend and labels all fixtures synthetic. Live course retrieval requires an independently deployed, reachable backend that implements [API_CONTRACT.md](API_CONTRACT.md). Set the server-side Vercel environment variable `SEARCH_API_URL` to that service's complete HTTPS search endpoint, then redeploy. Do not use localhost or a Docker service hostname in Vercel. No backend keys or URLs are embedded in client-side JavaScript.

If `SEARCH_API_URL` is absent, the function returns an explicit `SEARCH_NOT_CONFIGURED` response and the interface offers the sample search. It never silently replaces a live request with fixtures. Hosting this frontend is not evidence that real retrieval works.

## CLI

From this directory:

```sh
npx vercel login
npx vercel link --project wayfind-ac215
npx vercel deploy
# Verify the preview, then publish:
npx vercel deploy --prod
```

Use the existing project/scope selected by `vercel link`. The local `.vercel/` directory and environment files are ignored by Git. `.vercelignore` excludes environment files, tests, screenshots, and local environments from uploads.

For Git-based deployment later, choose repository `Charlottttttte/WayFind-ac215`, Root Directory `frontend`, and the branch containing this implementation. The implementation is currently in the draft frontend PR; `main` contains only its placeholder until the team merges it. Connecting the Git repository is optional for CLI deployment.

## Verify

- Open `/`; verify CSS, JavaScript, and the sample-search button load.
- Sample results must show a synthetic-preview badge and fixture dataset version.
- `POST /search` with no configured backend returns HTTP 503 and `SEARCH_NOT_CONFIGURED`.
- `GET /api/search` returns 405; it does not expose local files.
- After the real backend is configured, run all five team acceptance queries and save evidence.

Local preview: `python3 server.py`, then open http://127.0.0.1:8080. Opening `static/index.html` directly as a file cannot run the API and may block JavaScript modules.

References: [Vercel Python file-based functions](https://vercel.com/docs/functions/runtimes/python/api-directory), [Vercel project configuration](https://vercel.com/docs/project-configuration/vercel-json).
