Sync vs Async — Implementation Guidance for Astro Generation

Purpose
- Explain trade-offs between synchronous (Sync) and asynchronous (Async) server workflows for the `POST /api/astro/generate` feature, show recommended API shapes, UX patterns, operational impacts, and provide a migration plan from Sync → Async.

1. Summary — When to use which
- Sync: request-response completes with the final result in the HTTP response. Use for short-running work (recommended median latency < 10s) and low concurrency. Easier to implement and debug.
- Async: request enqueues a job and returns immediately with a job id; client polls or receives push updates. Use for long-running, variable, or CPU-heavy workloads and higher concurrency.

2. Key trade-offs
- Latency & UX: Sync gives immediate result but may block the client for the duration; Async improves perceived responsiveness and allows background processing.
- Server behavior & reliability: Sync ties up web workers/threads/processes; Async lets a short-lived request enqueue a job and frees web workers quickly.
- Complexity: Sync is simpler to implement; Async requires broker, result store, lifecycle management, and client-side polling or push.

3. Recommended API shapes

Sync (MVP)
- Endpoint: `POST /api/astro/generate`
- Response 200: `{ snapshot: {...}, summary: "...", meta: { generated_at, processing_time_ms, engine_version } }`
- Errors: 4xx/5xx as usual.

Async (future)
- `POST /api/astro/generate` → 202 Accepted
  - Body: `{ jobId: "uuid", status_url: "/api/astro/jobs/:jobId" }`
- `GET /api/astro/jobs/:jobId` → 200 `{ jobId, status: pending|running|done|failed, progress, submitted_at, started_at?, finished_at?, result_url?, error? }`
- `GET /api/astro/jobs/:jobId/result` → 200 returns the `snapshot` when `status == done`.

4. Frontend UX patterns
- Sync flow (MVP):
  - Submit → show blocking modal/spinner and cancel option; disable submit button.
  - Show progress indicator with an estimated time (if available).
  - On success show `summary` and a Download link for full JSON.
- Async flow (future):
  - Submit → show non-blocking toast/notification and job status page.
  - Poll status endpoint with exponential backoff (1s,2s,4s,8s) or use SSE/WebSocket for push updates.
  - Allow user to navigate away and notify when job completes (in-app notification or email if enabled).

5. Migration plan: Sync → Async
- Phase A (now): Implement Sync endpoint and frontend integration. Add input validation, rate limiting, and a server-side timeout guard. Add caching by `input_hash` to return immediate results for repeated inputs.
- Phase B (refactor): Extract the Surya→Parasara runner into an importable service function `generate_snapshot(input) -> dict` with no sys.path hacks. Ensure deterministic outputs for same inputs.
- Phase C (async worker): Implement a job queue (Redis + RQ/Celery/Huey), worker that calls `generate_snapshot`, persists results to a result store (Postgres/Blob + metadata), and exposes `GET /api/astro/jobs/:jobId` and `GET /api/astro/jobs/:jobId/result` endpoints.
- Phase D (frontend): Update frontend to POST and accept 202/jobId, implement polling or SSE, and keep the old Sync UI as a fallback for cached/fast runs.

6. Operational notes
- Timeouts: set web server timeout (nginx/gunicorn) below the worker max job time so web requests never hang.
- Worker sizing: CPU-bound tasks → prefer process-based workers equal to CPU cores per worker host.
- Caching: store by stable input hash (dob+time+lat+lon+tz+ayanamsa+house_system) to serve repeat requests instantly.
- Retention: store snapshots for a configurable TTL; delete after TTL and notify users where appropriate.

7. Testing & QA
- Unit test `generate_snapshot` with mocked Surya outputs (fast). Integration test that calls `POST /api/astro/generate` and asserts 200 with expected schema.
- When adding Async, add job lifecycle tests (enqueue, run, complete, error). Add E2E Playwright scenario that uses a mocked worker for CI.

8. Acceptance criteria for Sync MVP
- Frontend form submits valid input and receives `snapshot` + `summary` within acceptable time for developer environment (< 10s typical).
- Server performs validation, geocoding, timezone resolution, and calls `generate_snapshot` in-process without sys.path hacks.
- A cached response is returned instantly for duplicate requests.

9. Rollback & failure handling
- If the Sync endpoint hits resource limits or frequent timeouts, revert client to async polling mode and surface maintenance message.

10. Next steps (actionable)
- Implement Sync MVP using `generate_snapshot` service and wire `POST /api/astro/generate` to it.
- Add monitoring for processing latency and queue length; if P95 > 10s or queue/backlog increases, accelerate Async rollout.
