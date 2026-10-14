# Proposed MS2 search contract

**Status: pending agreement with Shravya.** This documents the shape consumed by the frontend, not an existing backend capability. Adjust this adapter and its tests when the backend contract is agreed.

## Request

Browser → frontend server: `POST /search`, `Content-Type: application/json`.
Frontend server → configured `SEARCH_API_URL`: same method and JSON fields.

```json
{
  "query": "Interests: interpretable ML\nCareer goal: PhD / research\nBackground: Statistics and Python\nCompleted courses: APCOMP 209A",
  "top_k": 5
}
```

The frontend requires nonblank interests. Profile values are plain query text, not backend filters or an instruction to exclude completed courses. The proxy requires a nonblank query and integer `top_k` from 1 to 20; it limits request size to 16 KiB. No browser-provided URL, authorization header, or extra field is forwarded.

## Response

```json
{
  "dataset_version": "<actual snapshot identifier>",
  "results": [
    {
      "course_id": "<stable ID from the dataset>",
      "title": "<course title>",
      "term": "<term recorded in the dataset>",
      "description": "<course description>",
      "context": "<passage returned by retrieval>",
      "source_urls": ["https://example.com/replace-with-actual-source"],
      "retrieved_at": "<source retrieval date>",
      "missing_or_uncertain_fields": ["<unresolved field or condition>"]
    }
  ]
}
```

`results` is required; `[]` means no matches. Each result requires nonempty string `course_id` and `title`. Other fields are optional: missing values display as unknown. Context must be retrieved evidence, not a frontend-written relevance explanation. Keep original retrieval order. If the data pipeline stores semicolon-delimited strings, the backend adapter must convert sources and uncertainty fields to arrays. Reconcile numeric course IDs versus catalog codes with John and Shravya before live verification.

The frontend permits only absolute HTTP(S) source URLs without embedded credentials. It displays all text via `textContent`. This is format validation, not verification of source truth or course eligibility.

## Failures and limits

The browser aborts after 15 seconds. The proxy uses a 12-second upstream timeout and a 2 MB response limit. Invalid request JSON returns 400; unsupported content type 415; invalid request size 413. Upstream HTTP errors/invalid responses return 502, and unavailable services/timeouts/rate limits return 503. The UI shows a retry message and preserves form input without exposing raw backend errors or returning mock data.

## Integration gate

- [ ] Shravya agrees on endpoint, method, fields, IDs, timeout expectations, and error semantics.
- [ ] Tavish confirms shared-network backend service name and port.
- [ ] John supplies the snapshot ID and source metadata that the API returns.
- [ ] Run Ming's five acceptance queries against the real pipeline and save input/output plus failures.
- [ ] Another team member reproduces the UI-to-retrieval flow from a clean checkout.

Related issue: [#4](https://github.com/Charlottttttte/WayFind-ac215/issues/4).
