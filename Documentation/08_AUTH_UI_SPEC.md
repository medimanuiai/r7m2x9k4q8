# Auth UI Specification — Register, Login, Account

**Version:** 0.1 (Draft)
**Last Updated:** 2026-06-01
**Status:** 🟡 In Review

This document covers the frontend UI specification for authentication-related pages in the Jyothishyam app:
- Register (`/register`)
- Login (`/login`)
- Account / Profile maintenance (`/account`)

It describes UX flows, form fields, validation rules, error states, accessibility requirements, API contracts used, and testing guidance.

---

## 1. Goals

- Provide a secure, accessible, and user-friendly registration and login experience.
- Ensure clear validation and error handling to reduce user friction.
- Minimize accidental credential exposure and follow best practices for token handling.
- Provide a lightweight profile page for users to update display name and avatar.

---

## 2. Routes & Components

- `GET /register` → `frontend/app/(auth)/register/page.tsx` (`RegisterPage`)
- `GET /login` → `frontend/app/(auth)/login/page.tsx` (`LoginPage`)
- `GET /account` → `frontend/app/(auth)/account/page.tsx` (`AccountPage`)

Shared components and utilities:
- `lib/api/client.ts` — base API client (attaches auth header, handles refresh)
- `lib/store/authStore.ts` — Zustand store for `user`, `tokens`, `balance` (TBD)
- `components/ui/*` — shared form inputs, buttons, toasts

---

## 3. Register Page — UX & Behavior

### 3.1 Purpose
Allow new users to create an account using email/password. On success, backend issues tokens and the user is redirected to login or dashboard.

### 3.2 URL
`/register`

### 3.3 Layout & Visuals
- Centered card, max width 420px
- Title: "Create your account"
- Subtext: short benefit statement and note about signup bonus
- Form fields stacked vertically with clear labels
- Primary CTA: "Create account"
- Secondary link: "Already have an account? Log in"

### 3.4 Fields (client-side names)
- `name` (string, required)
- `email` (string, required)
- `password` (string, required)
- `confirmPassword` (string, required)
- `acceptTos` (boolean, required)

### 3.5 Validation Rules
Client-side validation before submit:
- `name`: 2–100 characters
- `email`: valid email regex `^\S+@\S+\.\S+$`
- `password`: min 8 characters; recommend check for 1 uppercase, 1 lowercase, 1 number; show hint but final enforcement is server-side
- `confirmPassword`: must match `password`
- `acceptTos`: must be true

On failed validation show inline error message near the control and an alert summary at the top.

### 3.6 API Mapping
- Endpoint: `POST /api/v1/auth/register`
- Payload:
```json
{ "name": "...", "email": "...", "password": "..." }
```
- Success: HTTP 201 with `data.user` + tokens (or backend may set cookies)
- Errors: `EMAIL_ALREADY_EXISTS` (409), `WEAK_PASSWORD` (400)

Client behavior on success:
- Prefer backend-set auth cookie (httpOnly refresh token). If backend returns tokens in body, store `access_token` in memory/Zustand and refresh token via httpOnly cookie or secure storage.
- Redirect to `/login` or `/dashboard` depending on product choice. Current pages redirect to `/login`.

### 3.7 Edge Cases & UX
- If `EMAIL_ALREADY_EXISTS`, display inline help: "An account with that email already exists — try logging in or reset your password." with a link to `/login` and `/forgot-password`.
- For network errors show a dismissible toast: "Network error, please try again." with retry button.
- Disable submit while request is in-flight and show loading indicator.

### 3.8 Accessibility
- All inputs have associated `<label for>`.
- Use `aria-invalid="true"` on invalid inputs and `aria-describedby` linking to error message IDs.
- Keyboard focus order is logical; focus moves to the first invalid field on submit failure.
- Contrast and sizes meet AA standards.
- Terms link opens in same tab; mark checkbox with `aria-required`.

---

## 4. Login Page — UX & Behavior

### 4.1 Purpose
Authenticate existing users using email/password. Support "remember me" behavior and show password reset link.

### 4.2 URL
`/login`

### 4.3 Layout & Visuals
- Centered card, similar styling to register
- Title: "Welcome back"
- Subtext: "Log in to access your charts and AI readings"
- Fields: email, password, remember me checkbox
- CTA: "Sign in"
- Link: "Forgot?" pointing to `/forgot-password`

### 4.4 Fields
- `email` (string, required)
- `password` (string, required)
- `remember` (boolean, optional)

### 4.5 Validation
- Basic client-side: required and email pattern
- On submit send request to `POST /api/v1/auth/login`

### 4.6 API Mapping
- Endpoint: `POST /api/v1/auth/login`
- Payload:
```json
{ "email": "...", "password": "...", "remember": true }
```
- Success: HTTP 200 with `data.user`, `access_token`, `refresh_token` (or server-set cookie)
- Error codes: `INVALID_CREDENTIALS` (401), `ACCOUNT_INACTIVE` (401)

Client behavior on success:
- If server sets httpOnly refresh cookie and returns `access_token`, store access token in memory (Zustand) and call `GET /api/v1/auth/me` to fetch profile and credit balance.
- If server returns both tokens in body, store `access_token` in memory and `refresh_token` in secure cookie (preferably server set cookie).
- Redirect to last-intent path (if present) or `/dashboard`.

### 4.7 UX Notes
- After several failed attempts (as indicated by server), show CAPTCHA or rate-limited message (server-driven).
- If `ACCOUNT_INACTIVE`, display clear message and link to support.

### 4.8 Accessibility
- See Register page accessibility rules.
- `Forgot password` link has descriptive text and is focusable.

---

## 5. Account (Profile) Page — UX & Behavior

### 5.1 Purpose
Allow users to view and update basic profile data: display name and avatar URL, and access password change endpoint.

### 5.2 URL
`/account` (protected route — requires auth)

### 5.3 Layout & Visuals
- Left/top: heading "Account"
- Form: Name, Avatar URL, Save button
- Details: Email (readonly), Member since
- Security: link to `/change-password`

### 5.4 Data Loading
- On mount call `GET /api/v1/auth/me` to fetch `user` object.
- Show skeleton loader while fetching.

### 5.5 Fields & Validation
- `name`: required, 2–100 chars (client-side enforce)
- `avatar_url`: optional, must be a valid URL if provided (basic regex or URL constructor check)

### 5.6 API Mapping
- `GET /api/v1/auth/me` — returns current user
- `PATCH /api/v1/users/me` — payload `{ name?: string, avatar_url?: string }` — returns updated user

### 5.7 Save Flow
- Optimistic UI: prefer to wait for server response and then show success message. Show inline validation errors from server if any.
- Disable Save while request is in-flight.

### 5.8 Security
- Email is read-only; do not allow changing email from this page (future endpoint with verification flow).
- If backend returns 401 on `GET /auth/me`, redirect to `/login`.

### 5.9 Accessibility
- Form controls labeled, `aria-live` region for success/error messages.

---

## 6. Client-side Considerations

### 6.1 `authStore` (Zustand) — suggested shape
```ts
interface AuthState {
  user: User | null;
  accessToken: string | null; // short-lived
  isAuthenticated: boolean;
  creditBalance: number | null;

  setUser: (u: User | null) => void;
  setAccessToken: (t: string | null) => void;
  logout: () => Promise<void>;
}
```

- Store tokens in memory; prefer `httpOnly` cookie for refresh tokens set by backend.
- On app load, attempt `GET /api/v1/auth/me` to rehydrate `user`. If 401 and refresh cookie exists, attempt refresh via `POST /api/v1/auth/refresh`.

### 6.2 API Client Behavior (`lib/api/client.ts`)
- Attach `Authorization: Bearer <accessToken>` header when `accessToken` present.
- On 401 responses attempt a single token refresh (call `POST /api/v1/auth/refresh`) and retry request once.
- On 402 (INSUFFICIENT_CREDITS) bubble up to UI to show credit purchase CTA.
- Expose helper `api.post('/auth/login', body)` etc.

### 6.3 Security Notes
- Never store refresh tokens in `localStorage` unless strictly necessary and understood.
- Use `SameSite=Strict`, `Secure`, `HttpOnly` cookies for refresh tokens where possible.

---

## 7. Error Handling & UX Messages

- Generic network error: "Network error. Please check your connection and try again."
- Validation error mapping: display server-field messages next to inputs.
- Account exists: "An account with that email already exists — Log in or reset your password."
- Rate limit: "Too many attempts. Please wait a few minutes and try again."

---

## 8. Accessibility Checklist

- All inputs have labels and keyboard accessible.
- Error text readable by screen readers (`aria-live` polite region for form-level messages).
- Focus moves to the first invalid field after submit failure.
- Buttons have discernible text (no icons-only primary CTAs).
- Contrast ratio of text >= 4.5:1 for body text.

---

## 9. Automated Tests (Suggested)

Unit / integration tests to add:
- Register page
  - Valid form submits calls `POST /auth/register` with correct payload
  - Invalid email shows inline error
  - Password mismatch prevents API call
  - Server `EMAIL_ALREADY_EXISTS` displays help text
- Login page
  - Valid credentials route to `/dashboard`
  - Invalid credentials show error
  - Remember checkbox toggles behavior (if implemented)
- Account page
  - Loads `GET /auth/me` and populates fields
  - `PATCH /users/me` called on Save with changed fields

E2E tests (Cypress/Playwright):
- Happy path: register → login → load account → update name
- Error path: register with existing email → show message

---

## 10. Developer Notes

- Keep form components reusable; extract `TextField`, `PasswordField`, `Checkbox` to `components/ui`.
- Centralize validation rules in `lib/utils/validators.ts` (Zod schemas)
- Use React Query for `GET /auth/me` and profile mutations for caching and invalidation.
- Ensure pages work when JS is disabled (basic HTML form fallback) is not required for v1 but document progressive enhancement for later.

---

## 11. Open Decisions

- Where to redirect after registration: `/login` (current) vs auto login → `/dashboard` (future)
- `remember` behavior: persist access token in secure cookie or rely solely on refresh cookie
- Password strength feedback depth (basic hint vs live entropy meter)

---

*End of Auth UI specification (draft). Update this file when UI or API contract changes.*
