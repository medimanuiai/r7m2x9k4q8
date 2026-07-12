# Jyothishyam — Database Schema Specification

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Database:** PostgreSQL 15+
**ORM:** SQLAlchemy 2.x (Python) / Prisma (if Node.js used)

---

## 1. Design Principles

- All primary keys are UUIDs (not integer sequences) for security and future multi-region support.
- All timestamps are stored as `TIMESTAMPTZ` (UTC). Frontend is responsible for timezone display.
- Soft deletes: sensitive records (users, charts) use `deleted_at` instead of hard DELETE.
- The `credit_ledger` table is **append-only** — no UPDATE or DELETE ever. Balance is computed from sum.
- JSON columns (chart data) stored as `JSONB` for indexing support.
- All foreign keys have explicit ON DELETE rules defined.

---

## 2. Entity Relationship Diagram (Logical)

```
users
  │
  ├──< birth_charts
  │         │
  │         └──< ai_questions
  │                   │
  │                   └──< ai_answers
  │
  ├──< compatibility_profiles
  │
  ├──< credit_ledger
  │
  └──< transactions
```

---

## 3. Table Definitions

---

### 3.1 `users`

Stores registered user accounts.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique user identifier |
| `name` | `VARCHAR(100)` | NOT NULL | Display name |
| `email` | `VARCHAR(255)` | NOT NULL, UNIQUE | Login email |
| `password_hash` | `TEXT` | NULLABLE | bcrypt hash; NULL if OAuth-only user |
| `role` | `VARCHAR(20)` | NOT NULL, DEFAULT 'user' | 'user' or 'admin' |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Account status |
| `email_verified` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | Email verification status |
| `oauth_provider` | `VARCHAR(50)` | NULLABLE | 'google', 'apple', or NULL |
| `oauth_provider_id` | `VARCHAR(255)` | NULLABLE | Provider's user ID |
| `avatar_url` | `TEXT` | NULLABLE | Profile picture URL |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Account creation time |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Last update time |
| `deleted_at` | `TIMESTAMPTZ` | NULLABLE | Soft delete timestamp |

**Indexes:**
- `UNIQUE (email)` where `deleted_at IS NULL`
- `INDEX (oauth_provider, oauth_provider_id)`

**Rules:**
- `password_hash` must be NULL when `oauth_provider` is set, and vice versa.
- `role` enum enforced at application layer.

---

### 3.2 `birth_charts`

Stores user birth charts with computed chart data.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique chart ID |
| `user_id` | `UUID` | NOT NULL, FK → users.id ON DELETE CASCADE | Owner |
| `label` | `VARCHAR(100)` | NOT NULL | User-given name for the chart (e.g., "My Chart", "Mom") |
| `person_name` | `VARCHAR(100)` | NOT NULL | Person's actual name |
| `dob` | `DATE` | NOT NULL | Date of birth (YYYY-MM-DD) |
| `tob` | `TIME` | NOT NULL | Time of birth (HH:MM:SS local) |
| `tob_unknown` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | True if birth time is unknown/approximate |
| `place_name` | `VARCHAR(255)` | NOT NULL | City/place of birth (user-entered) |
| `latitude` | `NUMERIC(10,6)` | NOT NULL | Geocoded latitude |
| `longitude` | `NUMERIC(10,6)` | NOT NULL | Geocoded longitude |
| `timezone` | `VARCHAR(100)` | NOT NULL | IANA timezone string (e.g., "Asia/Kolkata") |
| `ayanamsa` | `VARCHAR(50)` | NOT NULL, DEFAULT 'LAHIRI' | Ayanamsa used (Lahiri, Raman, KP, etc.) |
| `chart_json` | `JSONB` | NOT NULL | Full chart computation result |
| `is_primary` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | User's primary/own chart |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Chart creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Last update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | NULLABLE | Soft delete |

**Indexes:**
- `INDEX (user_id)` 
- `INDEX (user_id, is_primary)`
- `GIN INDEX (chart_json)` for JSONB queries

**`chart_json` Structure:**
```json
{
  "ascendant": {
    "sign": "Aries",
    "sign_number": 1,
    "degree": 14.52,
    "nakshatra": "Ashwini",
    "pada": 2
  },
  "planets": [
    {
      "name": "Sun",
      "symbol": "☉",
      "longitude": 283.45,
      "sign": "Capricorn",
      "sign_number": 10,
      "house": 10,
      "degree": 13.45,
      "nakshatra": "Shravana",
      "pada": 2,
      "is_retrograde": false,
      "is_combust": false,
      "dignity": "exalted"
    }
  ],
  "houses": [
    {
      "number": 1,
      "sign": "Aries",
      "sign_number": 1,
      "degree_start": 14.52
    }
  ],
  "navamsa": {
    "planets": [],
    "ascendant": {}
  },
  "dashas": {
    "current_maha_dasha": {
      "planet": "Moon",
      "start_date": "2020-01-15",
      "end_date": "2030-01-15"
    },
    "current_antar_dasha": {
      "planet": "Mars",
      "start_date": "2025-03-01",
      "end_date": "2026-10-01"
    },
    "maha_dasha_sequence": []
  },
  "yogas": [
    {
      "name": "Gajakesari Yoga",
      "description": "Moon and Jupiter in mutual kendras",
      "is_present": true,
      "strength": "strong"
    }
  ],
  "computed_at": "2026-05-31T10:00:00Z",
  "engine_version": "1.0.0",
  "ayanamsa_value": 24.1234
}
```

---

### 3.3 `compatibility_profiles`

Stores other people's birth details added by a user for compatibility checks.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique profile ID |
| `user_id` | `UUID` | NOT NULL, FK → users.id ON DELETE CASCADE | Who added this profile |
| `person_name` | `VARCHAR(100)` | NOT NULL | Person's name |
| `relationship_type` | `VARCHAR(50)` | NOT NULL | 'love', 'business', 'friendship', 'family' |
| `dob` | `DATE` | NOT NULL | Date of birth |
| `tob` | `TIME` | NULLABLE | Time of birth (optional for compatibility) |
| `tob_unknown` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | True if time unknown |
| `place_name` | `VARCHAR(255)` | NOT NULL | Place of birth |
| `latitude` | `NUMERIC(10,6)` | NOT NULL | Geocoded latitude |
| `longitude` | `NUMERIC(10,6)` | NOT NULL | Geocoded longitude |
| `timezone` | `VARCHAR(100)` | NOT NULL | IANA timezone |
| `chart_json` | `JSONB` | NOT NULL | Computed chart for this profile |
| `avatar_url` | `TEXT` | NULLABLE | Optional photo |
| `notes` | `TEXT` | NULLABLE | User's private notes |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Created timestamp |
| `deleted_at` | `TIMESTAMPTZ` | NULLABLE | Soft delete |

**Indexes:**
- `INDEX (user_id)`
- `INDEX (user_id, relationship_type)`

---

### 3.4 `ai_questions`

Stores every question a user asks the AI engine.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique question ID |
| `user_id` | `UUID` | NOT NULL, FK → users.id ON DELETE CASCADE | Who asked |
| `chart_id` | `UUID` | NULLABLE, FK → birth_charts.id ON DELETE SET NULL | Chart used as context |
| `question_text` | `TEXT` | NOT NULL | The user's raw question |
| `question_type` | `VARCHAR(50)` | NOT NULL, DEFAULT 'general' | 'general', 'compatibility', 'daily', 'weekly', 'monthly', 'horoscope' |
| `context_json` | `JSONB` | NULLABLE | Snapshot of chart context sent to AI |
| `credits_charged` | `INTEGER` | NOT NULL | Credits deducted for this question |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Question timestamp |

**Indexes:**
- `INDEX (user_id)`
- `INDEX (user_id, created_at DESC)`
- `INDEX (chart_id)`

---

### 3.5 `ai_answers`

Stores the AI-generated answer to each question (1:1 with ai_questions).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique answer ID |
| `question_id` | `UUID` | NOT NULL, UNIQUE, FK → ai_questions.id ON DELETE CASCADE | Link to question |
| `answer_text` | `TEXT` | NOT NULL | Full AI response |
| `model_used` | `VARCHAR(100)` | NOT NULL | e.g., 'gpt-4o-mini', 'claude-3-haiku' |
| `provider` | `VARCHAR(50)` | NOT NULL | 'openai', 'anthropic', 'google' |
| `prompt_tokens` | `INTEGER` | NOT NULL | Input token count |
| `completion_tokens` | `INTEGER` | NOT NULL | Output token count |
| `total_tokens` | `INTEGER` | NOT NULL | Sum of prompt + completion |
| `latency_ms` | `INTEGER` | NULLABLE | Time taken for AI call in milliseconds |
| `is_flagged` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | Admin moderation flag |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Answer timestamp |

**Indexes:**
- `INDEX (question_id)`

---

### 3.6 `credit_ledger`

Append-only ledger of all credit transactions. **Never update or delete rows.**

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Unique ledger entry ID |
| `user_id` | `UUID` | NOT NULL, FK → users.id ON DELETE CASCADE | User |
| `entry_type` | `VARCHAR(20)` | NOT NULL | 'credit' (added) or 'debit' (used) |
| `credits_delta` | `INTEGER` | NOT NULL | Positive for credit, negative for debit |
| `balance_after` | `INTEGER` | NOT NULL | Running balance snapshot after this entry |
| `reason` | `VARCHAR(100)` | NOT NULL | 'purchase', 'ai_question', 'compatibility_check', 'horoscope_reading', 'admin_grant', 'refund', 'signup_bonus' |
| `reference_id` | `UUID` | NULLABLE | FK to transaction.id or ai_question.id |
| `reference_type` | `VARCHAR(50)` | NULLABLE | 'transaction', 'ai_question' |
| `note` | `TEXT` | NULLABLE | Human-readable note |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Ledger entry timestamp |

**Indexes:**
- `INDEX (user_id)`
- `INDEX (user_id, created_at DESC)`

**Business Rule:** `balance_after` must never go below 0. Backend enforces this before writing.

---

### 3.7 `transactions`

Records all Stripe payment transactions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Internal transaction ID |
| `user_id` | `UUID` | NOT NULL, FK → users.id ON DELETE CASCADE | User who paid |
| `stripe_session_id` | `VARCHAR(255)` | NOT NULL, UNIQUE | Stripe Checkout Session ID |
| `stripe_payment_intent_id` | `VARCHAR(255)` | NULLABLE | Stripe Payment Intent ID |
| `pack_name` | `VARCHAR(50)` | NOT NULL | 'starter', 'standard', 'pro' |
| `amount_cents` | `INTEGER` | NOT NULL | Amount in cents (499, 999, 1999) |
| `currency` | `VARCHAR(10)` | NOT NULL, DEFAULT 'usd' | ISO currency code |
| `credits_purchased` | `INTEGER` | NOT NULL | Credits to be added (50, 150, 400) |
| `status` | `VARCHAR(20)` | NOT NULL, DEFAULT 'pending' | 'pending', 'completed', 'failed', 'refunded' |
| `webhook_received_at` | `TIMESTAMPTZ` | NULLABLE | When Stripe webhook confirmed payment |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Purchase initiation time |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Last status update |

**Indexes:**
- `INDEX (user_id)`
- `UNIQUE (stripe_session_id)`
- `INDEX (status)`

---

### 3.8 `refresh_tokens` *(Auth)*

Stores refresh tokens for JWT-based auth.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PK, DEFAULT gen_random_uuid() | Token ID |
| `user_id` | `UUID` | NOT NULL, FK → users.id ON DELETE CASCADE | User |
| `token_hash` | `TEXT` | NOT NULL, UNIQUE | bcrypt hash of the refresh token |
| `device_hint` | `VARCHAR(255)` | NULLABLE | User agent or device label |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | Expiry time (7 days from issue) |
| `revoked_at` | `TIMESTAMPTZ` | NULLABLE | If revoked, timestamp here |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, DEFAULT NOW() | Issue time |

**Indexes:**
- `INDEX (user_id)`
- `INDEX (token_hash)` where `revoked_at IS NULL`

---

## 4. Database Migrations Strategy

- Migrations managed by **Alembic** (Python/SQLAlchemy stack).
- Each migration file named: `YYYYMMDD_HHMMSS_short_description.py`
- Migrations run automatically on backend container startup in dev.
- Production migrations run as a separate pre-deploy step.
- No destructive migrations (DROP COLUMN) without a deprecation window.

---

## 5. Computed / Derived Values

These values are **never stored** — they are always computed at query time:

| Value | How Computed |
|---|---|
| User's current credit balance | `SELECT SUM(credits_delta) FROM credit_ledger WHERE user_id = ?` |
| Total AI questions asked | `SELECT COUNT(*) FROM ai_questions WHERE user_id = ?` |
| Total tokens used | `SELECT SUM(total_tokens) FROM ai_answers JOIN ai_questions ON ... WHERE user_id = ?` |
| Total amount spent | `SELECT SUM(amount_cents) FROM transactions WHERE user_id = ? AND status = 'completed'` |

---

## 6. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| DB1 | UUID vs ULID for primary keys | UUID (current) / ULID (time-sortable) | 🟡 Pending |
| DB2 | Store `balance_after` in ledger | Yes (current) / No (compute always) | 🟡 Pending |
| DB3 | Separate table for OAuth accounts | Yes (accounts table) / Current approach | 🟡 Pending |
| DB4 | Archiving old ai_answers | Partition by year / External storage | 🟡 Pending |

---

*This document is a living specification. Tables marked as final will have status updated to ✅.*
