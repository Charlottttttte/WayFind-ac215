# WayFind MS2 frontend

Owner: Akshaya. This component implements the proposal's profile form and a course-results screen for the MS2 retrieval slice. It uses plain HTML/CSS/JavaScript with a Python standard-library server, so there is no JavaScript build or runtime dependency installation. The Python server serves public assets and proxies requests to Shravya's retrieval API; it does not perform retrieval itself.

## Run locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this directory:

```sh
uv run --frozen server.py
```

Open http://127.0.0.1:8080. Equivalent dependency-free fallback: `python3 server.py`.

By default the server forwards `POST /search` to `http://127.0.0.1:8000/search`. Override the full endpoint URL:

```sh
SEARCH_API_URL=http://127.0.0.1:8000/search PORT=8080 uv run --frozen server.py
```

Enter interests and choose **Explore courses**. Live mode is the default. Under **Preview options**, explicitly select **Use synthetic sample results** to exercise successful, empty, and failed UI states without a backend. The preview fixtures are invented records named SAMPLE-101 and SAMPLE-202, not Harvard courses; they are independent of the query and are not retrieval evidence. Live errors never fall back to mock results.

## Run the component container

From this directory, with Docker Desktop/Engine running:

```sh
docker compose up --build
```

Open http://127.0.0.1:8080. Compose reads `.env` if present; `.env.example` shows optional settings. The default backend is on the host at `http://host.docker.internal:8000/search`. On Linux, the Compose `host-gateway` mapping supplies that hostname. Stop with `docker compose down`.

For Tavish's root Compose pipeline, use build context `./frontend`, container port `8080`, and set `SEARCH_API_URL=http://<backend-service-name>:<backend-port>/search`. Containers must share a network. Confirm the actual service name and port with the backend owner. The browser calls same-origin `/search`, so it does not resolve Docker hostnames or require CORS configuration.

The container has pinned Python/uv image tags, a committed uv lockfile, a non-root user, and a `/health` endpoint. Health confirms only that the frontend serves requests, not that retrieval is available. This standard-library server is intended for the local MS2 demo, not an internet production deployment.

## Host on Vercel

See [VERCEL.md](VERCEL.md) for deployment and backend configuration. Use `frontend` as the project root. The hosted frontend provides an explicit sample search; real retrieval still requires the deployed backend endpoint.

## API and data boundary

See [API_CONTRACT.md](API_CONTRACT.md). The contract is a **frontend proposal pending agreement with Shravya**, because the backend currently contains only a README. The UI preserves the result order and displays returned context, source URLs, dataset version, retrieval date, and uncertainty. Missing metadata stays visibly unknown; it is not inferred.

Profile fields are combined into a query, not enforced as filters. Completed courses do not automatically exclude matches. Degree validation, prerequisite checking, roadmap generation, trained ranking, and mentor matching are outside this MS2 frontend.

## Checks

From the repository root, with Node.js 18+ and Python 3.12+:

```sh
node --test frontend/tests/api.test.mjs
python3 -m unittest discover -s frontend/tests -v
git diff --check
```

The Python tests start temporary loopback HTTP servers and need permission to bind local ports. They verify a stub contract, not the real retrieval pipeline. See [VERIFICATION.md](VERIFICATION.md) for observed results and remaining checks.

Manual checks: submit a whitespace-only query; run all three synthetic scenarios; retry after error; deselect synthetic mode and verify a backend-unavailable error; repeat at a narrow viewport. Confirm inputs remain editable, old results clear, status is announced, and unsafe source schemes cannot become links.

Tracking: [UI #3](https://github.com/Charlottttttte/WayFind-ac215/issues/3), [API #4](https://github.com/Charlottttttte/WayFind-ac215/issues/4), [states/tests #5](https://github.com/Charlottttttte/WayFind-ac215/issues/5), [container integration #6](https://github.com/Charlottttttte/WayFind-ac215/issues/6).
