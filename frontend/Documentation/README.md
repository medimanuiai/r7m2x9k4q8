Frontend Astro Integration — Documentation

Purpose
- Describe the frontend changes required to capture user birth details (DOB, time, place) and submit them to the backend SuryaSiddhanta→Parasara pipeline.

Audience
- Frontend engineers, QA, product owners.

What this folder contains
- `api_spec.md` — API contract for the new endpoint used by the frontend.
- `tasks.md` — Concrete frontend tasks, owners, estimates, and statuses.

High-level flow
- Authenticated user navigates to an "Astrology" page after login.
- The page presents a form: Date, Time, Place (autocomplete), optional lat/lon and timezone override.
- On submit the client POSTs to `POST /api/astro/generate` and displays a summary and link to full explainability JSON.

Note: The backend now returns two useful artifacts in the response JSON:
- `surya_chart`: the raw NDAstro (Surya Siddhanta) chart including `planets`, `lagna`, `nakshatra` and basic houses/aspects when available. The frontend displays this in the Result view for debugging and inspection.
- `meta.generated_at`: an ISO timestamp indicating when the snapshot was generated; shown in the UI under Engine/Generated.

Dev route
- The authenticated UI is available at `/account/astro` within the authenticated area of the Next.js app (path: `frontend/app/(auth)/account/astro/page.tsx`).

Python runner
- The dev Next.js API route calls the Python runner to produce real Parasara snapshots. Ensure the Python executable in your development environment points to the project's virtualenv by setting `PYTHON_EXECUTABLE` (example Windows):

```powershell
$env:PYTHON_EXECUTABLE = 'C:\path\to\jyothishyam_env\Scripts\python.exe'
npm run dev
```

If `PYTHON_EXECUTABLE` is not set, the route will attempt to use the `python` on PATH which may not have required packages (Skyfield, ndastro_engine, etc.).

UX considerations
- Provide clear privacy notice and a consent checkbox before submission.
- Allow timezone override and manual lat/lon entry for advanced users.
CSS / Login styling
- Global stylesheet: `frontend/styles/globals.css` is imported by `app/layout.tsx` and provides the login screen styles (variables, `.hero-bg`, `.auth-card`, `.pill-btn`, `.input-with-icon`, etc.).
- Some components use utility classes like `text-text-primary` and `text-text-muted`; these are defined as compatibility helpers in `globals.css` so the login screen works even when Tailwind utilities are not present.
