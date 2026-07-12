API: POST /api/astro/generate

Summary
- Authenticated endpoint used by the frontend to request a SuryaSiddhanta chart + Parasara snapshot for a given birth record.

Request JSON
- `dob` (string, required): ISO date `YYYY-MM-DD`
- `time` (string, required): local time `HH:MM` (24h)
- `place` (string, optional): free-text place name (used for geocoding)
- `lat` (number, optional): decimal latitude (preferred if provided)
- `lon` (number, optional): decimal longitude (preferred if provided)
- `tz` (string, optional): IANA timezone name (e.g., `Asia/Kolkata`) — if omitted, server derives it from place/latlon
- `consent` (boolean, required): user consent to process/store birth data (false → ephemeral only)

Response (200)
- `snapshot` (object): Parasara snapshot result (domains, explainability, diagnostics)
- `surya_chart` (object, optional): Raw NDAstro/SuryaSiddhanta chart JSON with `planets`, `lagna`, `houses`, `nakshatra` fields. Useful for debugging and direct NDAstro inspection in the UI.
- `summary` (string): short human-friendly summary for UI
- `meta` (object): `{ generated_at: ISO8601, processing_time_ms: int, engine_version: string }`

Errors
- 400: invalid input (validation error details)
- 401: authentication required
- 422: unable to geocode place or resolve timezone
- 503: backend busy / timeout (if processing is synchronous and timed out)

Notes for frontend
- Expect snapshot to be large; fetch full JSON via streaming or show truncated preview and a download link.
- For long-running processing consider polling an async job endpoint; the UI should show loading and allow cancellation.
