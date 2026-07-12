# Frontend Tasks — SuryaSiddhanta → Parasara integration

Owner tags are placeholders; update owners and estimates as needed.


- FE-Task#001 — Add `AstroForm` page/component — owner: @frontend — estimate: 0.5d — acceptance: authenticated route displays form with fields `dob`, `time`, `place`, optional `lat`, `lon`, `tz`; form validates inputs. — status: Completed

- FE-Task#002 — Place autocomplete & geocode integration — owner: @frontend — estimate: 1d — acceptance: `place` field supports autocomplete (Nominatim/Places) and returns lat/lon; UI shows detected timezone; exposes manual override. — status: Completed

- FE-Task#003 — API integration (sync) — owner: @frontend — estimate: 0.5d — acceptance: form POSTs to `POST /api/astro/generate`, handles success (renders `summary` and download link) and error states. — status: Completed

- FE-Task#004 — Async job flow (optional) — owner: @frontend — estimate: 1d — acceptance: support submission that returns `jobId`; client polls `/api/astro/status/:id` and fetches `/api/astro/result/:id` when ready; UI shows progress. — status: Planned

  - Reminder: Implement Async job flow when user load increases or P95 processing time exceeds acceptable threshold. See `frontend/Documentation/sync_async.md` for migration plan and API shapes.

- FE-Task#005 — Result viewer component — owner: @frontend — estimate: 0.5d — acceptance: display compact domains summary and allow toggling full explainability JSON view/download. — status: Completed

- FE-Task#006 — Accessibility & localization — owner: @frontend — estimate: 0.5d — acceptance: form fields labeled, keyboard accessible, date/time localized; tooltips for privacy. — status: Not Started

- FE-Task#007 — Unit tests & component tests — owner: @qa — estimate: 0.5d — acceptance: unit tests for `AstroForm` validation and `ResultViewer` rendering. — status: Not Started

- FE-Task#008 — E2E smoke test — owner: @qa — estimate: 1d — acceptance: Playwright test that logs in, submits sample DOB/place/time, and verifies summary appears and snapshot download works (can mock backend in CI). — status: Planned

- FE-Task#009 — Docs & onboarding — owner: @frontend — estimate: 0.25d — acceptance: update `frontend/Documentation/README.md` and add a short how-to for devs. — status: In Progress

Priority: FE-Task#001 → FE-Task#002 → FE-Task#003 → FE-Task#005 are the MVP sequence. Decide sync vs async before implementing FE-Task#004.
