# Jyothishyam — Documentation Index

**Project:** Jyothishyam (AI-Driven Vedic Astrology Platform)
**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31

---

## Specification Documents

| # | Document | Description | Status |
|---|---|---|---|
| 00 | [Project Overview](./00_PROJECT_OVERVIEW.md) | Vision, tech stack, architecture, milestones | 🟡 In Review |
| 01 | [Database Schema](./01_DATABASE_SCHEMA.md) | All tables, columns, constraints, ERD, JSON structures | 🟡 In Review |
| 02 | [API Specifications](./02_API_SPECIFICATIONS.md) | All REST endpoints, request/response contracts, error codes | 🟡 In Review |
| 03 | [Astrology Engine](./03_ASTROLOGY_ENGINE_SPEC.md) | pyswisseph wrapper, planetary calculations, nakshatra/dasha logic | 🟡 In Review |
| 04 | [AI Engine](./04_AI_ENGINE_SPEC.md) | Provider abstraction, prompt templates, token tracking, safety | 🟡 In Review |
| 05 | [Credit & Payment](./05_CREDIT_AND_PAYMENT_SPEC.md) | Credit ledger, Stripe checkout, webhook handling, refunds | 🟡 In Review |
| 06 | [Frontend](./06_FRONTEND_SPEC.md) | Pages, components, state management, design system | 🟡 In Review |
| 07 | [Auth & Authorization](./07_AUTH_SPEC.md) | JWT, bcrypt, token refresh, security measures | 🟡 In Review |

## System-Level Docs

- SuryaSiddhanta system: `systems/SuryaSiddhanta/Documentation/SuryaSiddhanta_System.md` (astrology engine implementation & developer notes)


---

## Status Key

| Symbol | Meaning |
|---|---|
| 🟡 In Review | Draft — needs review and sign-off |
| ✅ Agreed | Finalized and locked |
| 🔴 Blocked | Waiting on a decision or dependency |
| 🔵 In Progress | Actively being built |

---

## Open Decisions Tracker

All major undecided items from all spec documents, consolidated:

| ID | Document | Decision | Status |
|---|---|---|---|
| D1 | Overview | Default AI provider (OpenAI / Anthropic / Gemini) | 🟡 Pending |
| D2 | Overview | Social login (Google/Apple) in Phase 1 | 🟡 Pending |
| D3 | Overview | North Indian vs South Indian chart style default | 🟡 Pending |
| D4 | Overview | Geocoding provider | 🟡 Pending |
| DB1 | Database | UUID vs ULID for primary keys | 🟡 Pending |
| DB2 | Database | Store `balance_after` in ledger or compute always | 🟡 Pending |
| AE1 | Astrology | Default house system (Whole Sign vs Placidus) | 🟡 Pending |
| AE2 | Astrology | Rahu/Ketu sign assignment (by system) | 🟡 Pending |
| AE3 | Astrology | Pratyantar dasha in Phase 1 | 🟡 Pending |
| AE4 | Astrology | Additional divisional charts (D3, D7, D10) | 🟡 Pending |
| AI1 | AI Engine | AI provider selection | 🟡 Pending |
| AI2 | AI Engine | Async AI calls with job queue (Celery) | 🟡 Pending |
| AI3 | AI Engine | Response streaming (SSE) | 🟡 Pending |
| PAY1 | Payments | Credit expiry policy | 🟡 Pending |
| PAY2 | Payments | Refund policy | 🟡 Pending |
| FE1 | Frontend | Chart style default | 🟡 Pending |
| FE2 | Frontend | Token storage (httpOnly cookie vs localStorage) | 🟡 Pending |
| FE3 | Frontend | AI response streaming | 🟡 Pending |
| AUTH1 | Auth | Refresh token storage on client | 🟡 Pending |
| AUTH2 | Auth | Email verification required at signup | 🟡 Pending |
| AUTH3 | Auth | Forgot password in Phase 1 | 🟡 Pending |

---

## How To Use These Docs

1. **Review each spec** — Read through each document and flag anything that needs changing.
2. **Resolve open decisions** — Go through the decisions tracker above, make a call on each one, and update the relevant spec.
3. **Lock sections** — When a section is agreed upon, mark it ✅ in both the spec and this index.
4. **Generate code** — Once a spec section is locked ✅, request the corresponding code module.

---

*This index is updated each time a new spec document is added or an existing one changes status.*
