Create a highly professional login screen and matching Node.js backend. Deliver a complete, production-ready scaffold with code, tests, and deployment notes. Follow these requirements:

Project scope

Tech stack: Node.js (>=18), Express, bcrypt, helmet, csurf, express-rate-limit, cookie-session or JWT, and a templating option (choose one): React + Vite or EJS. Include instructions for both options. 

Database: provide examples for MongoDB (Mongoose) and Postgres (Prisma).

Authentication flows: email+password, passwordless (magic link), passkeys/SSO hint, and optional MFA (TOTP). Emphasize UX clarity and minimal friction. 

UI and UX

Provide a pixel‑perfect responsive layout (desktop, tablet, mobile) with CSS variables, accessible color contrast, keyboard navigation, and ARIA attributes. Include microcopy for errors, success, and loading states. Add subtle motion for focus and submit states.





Include design tokens (colors, spacing, typography) and a dark mode variant.





Security and best practices

Server: input validation, password hashing with bcrypt, CSRF protection, secure cookies, HTTP headers via helmet, rate limiting, account lockout after repeated failures, and secure session/JWT handling. Provide code examples and configuration notes for production secrets and env variables. 

Explain tradeoffs between session cookies vs JWT and recommend one for typical web apps.

Deliverables

File structure and scaffold commands (npm scripts).

Frontend component(s) or EJS templates with CSS and minimal JS for client validation and animations.





Express routes: /login, /logout, /register, /forgot-password, /magic-link, /mfa-verify. Include middleware for auth and role checks.

Database models for users and sessions.

Unit and integration tests (Jest + Supertest) for auth flows and security checks.

Accessibility checklist and automated audit commands (axe-core).

Deployment notes for Vercel, Heroku, and Docker with environment variable examples.

README with acceptance criteria and rollback steps.

Acceptance criteria

Responsive across breakpoints.

WCAG AA contrast and keyboard operability.

Automated tests covering 90% of auth logic.

Rate limiting and CSRF enabled by default.

Optional variations

Provide a version using Tailwind CSS and one using vanilla CSS.





Security and UX checklist to include in output
Password hashing with bcrypt and salt rounds. 

CSRF tokens on state-changing forms. 

Clear error messages that avoid leaking whether an email exists