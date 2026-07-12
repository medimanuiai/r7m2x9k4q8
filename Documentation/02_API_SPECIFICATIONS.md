# Jyothishyam — API Specifications

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Base URL (dev):** `http://localhost:8000/api/v1`
**Base URL (prod):** `https://api.jyothishyam.com/api/v1`

---

## 1. General Conventions

### 1.1 Request Format
- All request bodies: `application/json`
- All responses: `application/json`
- Dates: ISO 8601 string (`YYYY-MM-DD`)
- Times: `HH:MM` or `HH:MM:SS` (24-hour, local time of birth)
- Timestamps: ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`)

### 1.2 Authentication
- Protected routes require header: `Authorization: Bearer <access_token>`
- Access token lifetime: **15 minutes**
- Refresh token lifetime: **7 days**
- Refresh endpoint: `POST /auth/refresh`

### 1.3 Standard Response Envelope

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-05-31T10:00:00Z"
  }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "You do not have enough credits to perform this action.",
    "details": {}
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-05-31T10:00:00Z"
  }
}
```

### 1.4 HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 402 | Payment Required (insufficient credits) |
| 403 | Forbidden (role mismatch) |
| 404 | Not Found |
| 409 | Conflict (e.g., email already registered) |
| 422 | Unprocessable Entity (Pydantic validation) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

### 1.5 Rate Limiting

| Endpoint Group | Limit |
|---|---|
| `/auth/*` | 10 requests / minute per IP |
| `/ai/ask` | 30 requests / hour per user |
| `/charts/*` | 60 requests / hour per user |
| All others | 120 requests / minute per user |

---

## Implementation Notes

- The birth chart calculation implementation is provided by the SuryaSiddhanta system (`systems/SuryaSiddhanta/ndastro_engine`). API implementers should call the service-level function `calculate_chart(birth_iso, lat, lon, ayanamsa)` (or the equivalent endpoint in the chart service) to obtain the chart JSON described in the `/charts` routes below. For testing and developer setup, see `systems/SuryaSiddhanta/Documentation/SuryaSiddhanta_System.md` and `tests/SuryaSiddhanta/Documentation/SuryaSiddhanta_Testing.md`.


## 2. Authentication Routes (`/auth`)

---

### `POST /auth/register`

Register a new user account.

**Auth required:** No

**Request Body:**
```json
{
  "name": "Arjun Nair",
  "email": "arjun@example.com",
  "password": "SecurePass123!"
}
```

**Validation Rules:**
- `name`: 2–100 characters
- `email`: valid email format, unique
- `password`: min 8 chars, at least 1 uppercase, 1 digit, 1 special char

**Response `201`:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "Arjun Nair",
      "email": "arjun@example.com",
      "role": "user",
      "created_at": "2026-05-31T10:00:00Z"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

**Error Codes:** `EMAIL_ALREADY_EXISTS`, `WEAK_PASSWORD`, `INVALID_EMAIL`

---

### `POST /auth/login`

Authenticate with email and password.

**Auth required:** No

**Request Body:**
```json
{
  "email": "arjun@example.com",
  "password": "SecurePass123!"
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "Arjun Nair",
      "email": "arjun@example.com",
      "role": "user"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "credit_balance": 50
  }
}
```

**Error Codes:** `INVALID_CREDENTIALS`, `ACCOUNT_INACTIVE`

---

### `POST /auth/refresh`

Exchange a refresh token for a new access token.

**Auth required:** No (refresh token in body)

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

**Error Codes:** `INVALID_REFRESH_TOKEN`, `TOKEN_EXPIRED`

---

### `POST /auth/logout`

Revoke the current refresh token.

**Auth required:** Yes

**Request Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200`:**
```json
{ "success": true, "data": { "message": "Logged out successfully." } }
```

---

### `GET /auth/me`

Get current authenticated user's profile.

**Auth required:** Yes

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Arjun Nair",
    "email": "arjun@example.com",
    "role": "user",
    "credit_balance": 45,
    "created_at": "2026-05-31T10:00:00Z"
  }
}
```

---

## 3. Birth Chart Routes (`/charts`)

---

### `POST /charts`

Create a new birth chart.

**Auth required:** Yes

**Request Body:**
```json
{
  "label": "My Chart",
  "person_name": "Arjun Nair",
  "dob": "1990-03-15",
  "tob": "06:45",
  "tob_unknown": false,
  "place_name": "Kochi, Kerala, India",
  "is_primary": true,
  "ayanamsa": "LAHIRI"
}
```

**Validation Rules:**
- `dob`: valid past date, not before 1800-01-01
- `tob`: HH:MM format; required if `tob_unknown` is false
- `ayanamsa`: one of `LAHIRI`, `RAMAN`, `KP`, `FAGAN_BRADLEY`
- `place_name`: geocoded server-side; returns error if not found

**Response `201`:**
```json
{
  "success": true,
  "data": {
    "chart": {
      "id": "uuid",
      "label": "My Chart",
      "person_name": "Arjun Nair",
      "dob": "1990-03-15",
      "tob": "06:45:00",
      "place_name": "Kochi, Kerala, India",
      "latitude": 9.9312,
      "longitude": 76.2673,
      "timezone": "Asia/Kolkata",
      "ayanamsa": "LAHIRI",
      "is_primary": true,
      "chart_json": { ... },
      "created_at": "2026-05-31T10:00:00Z"
    }
  }
}
```

**Error Codes:** `PLACE_NOT_FOUND`, `INVALID_DATE`, `INVALID_TIME`

---

### `GET /charts`

List all birth charts for the authenticated user.

**Auth required:** Yes

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Results per page (max 50) |

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "charts": [
      {
        "id": "uuid",
        "label": "My Chart",
        "person_name": "Arjun Nair",
        "dob": "1990-03-15",
        "place_name": "Kochi, Kerala, India",
        "is_primary": true,
        "created_at": "2026-05-31T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20
  }
}
```

---

### `GET /charts/{chart_id}`

Fetch a single birth chart with full chart JSON.

**Auth required:** Yes

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "chart": { ... }
  }
}
```

**Error Codes:** `CHART_NOT_FOUND`, `FORBIDDEN`

---

### `DELETE /charts/{chart_id}`

Soft-delete a birth chart.

**Auth required:** Yes

**Response `200`:**
```json
{ "success": true, "data": { "message": "Chart deleted." } }
```

---

## 4. AI Routes (`/ai`)

---

### `POST /ai/ask`

Ask an astrological question using a specific chart as context.

**Auth required:** Yes

**Rate limit:** 30 / hour per user

**Request Body:**
```json
{
  "chart_id": "uuid",
  "question": "Will I get a promotion this year based on my current dasha?",
  "question_type": "general"
}
```

**`question_type` values:** `general`, `daily`, `weekly`, `monthly`, `horoscope`

**Credit costs:**
- `general`: 1 credit
- `daily`: 1 credit
- `weekly`: 2 credits
- `monthly`: 3 credits
- `horoscope`: 10 credits

**Pre-call validation:**
1. Check user has sufficient credits → `402` if not
2. Verify chart belongs to user → `403` if not
3. Sanitize question text (strip prompt injection attempts)

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "question_id": "uuid",
    "answer": "Based on your current Moon Mahadasha and Mars Antardasha...",
    "model_used": "gpt-4o-mini",
    "tokens_used": 1243,
    "credits_charged": 1,
    "credit_balance_remaining": 44
  }
}
```

**Error Codes:** `INSUFFICIENT_CREDITS`, `CHART_NOT_FOUND`, `AI_SERVICE_UNAVAILABLE`, `RATE_LIMIT_EXCEEDED`

---

### `GET /ai/history`

Get the user's AI question and answer history.

**Auth required:** Yes

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `chart_id` | UUID | null | Filter by chart |
| `question_type` | string | null | Filter by type |
| `page` | integer | 1 | Page number |
| `per_page` | integer | 20 | Max 50 |

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "question_id": "uuid",
        "question_text": "Will I get a promotion...",
        "question_type": "general",
        "answer_text": "Based on your current Moon Mahadasha...",
        "model_used": "gpt-4o-mini",
        "tokens_used": 1243,
        "credits_charged": 1,
        "created_at": "2026-05-31T10:00:00Z"
      }
    ],
    "total": 15,
    "page": 1,
    "per_page": 20
  }
}
```

---

### `GET /ai/history/{question_id}`

Get a specific AI question and answer by ID.

**Auth required:** Yes

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "question_id": "uuid",
    "question_text": "...",
    "answer_text": "...",
    "model_used": "gpt-4o-mini",
    "prompt_tokens": 900,
    "completion_tokens": 343,
    "total_tokens": 1243,
    "credits_charged": 1,
    "created_at": "2026-05-31T10:00:00Z"
  }
}
```

---

## 5. Compatibility Routes (`/compatibility`)

---

### `POST /compatibility/check`

Run a compatibility analysis between two charts.

**Auth required:** Yes
**Credit cost:** 5 credits

**Request Body:**
```json
{
  "chart_id_1": "uuid",
  "chart_id_2": "uuid",
  "compatibility_type": "love",
  "question": "Are we compatible for marriage?"
}
```

**`compatibility_type` values:** `love`, `business`, `friendship`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "compatibility_score": 78,
    "compatibility_type": "love",
    "summary": "Strong Moon compatibility. Venus trine Jupiter indicates...",
    "categories": {
      "emotional": 85,
      "intellectual": 72,
      "physical": 75,
      "spiritual": 80
    },
    "kuta_scores": {
      "varna": 1,
      "vashya": 2,
      "tara": 3,
      "yoni": 3,
      "graha_maitri": 4,
      "gana": 5,
      "bhakoot": 6,
      "nadi": 8,
      "total": 32,
      "max": 36
    },
    "ai_analysis": "Based on Ashtakoot compatibility...",
    "credits_charged": 5,
    "credit_balance_remaining": 39
  }
}
```

---

### `POST /compatibility/profiles`

Add a compatibility profile (another person's birth details).

**Auth required:** Yes

**Request Body:**
```json
{
  "person_name": "Priya Menon",
  "relationship_type": "love",
  "dob": "1993-07-22",
  "tob": "09:30",
  "tob_unknown": false,
  "place_name": "Trivandrum, Kerala, India"
}
```

**Response `201`:** Created profile with computed chart JSON.

---

### `GET /compatibility/profiles`

List all compatibility profiles for the user.

**Auth required:** Yes

**Response `200`:** Array of profiles (without full chart_json for performance).

---

## 6. Payment Routes (`/payments`)

---

### `POST /payments/checkout`

Create a Stripe Checkout session for a credit pack.

**Auth required:** Yes

**Request Body:**
```json
{
  "pack": "standard"
}
```

**`pack` values:** `starter`, `standard`, `pro`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "checkout_url": "https://checkout.stripe.com/pay/cs_...",
    "session_id": "cs_...",
    "pack": "standard",
    "amount_cents": 999,
    "credits": 150
  }
}
```

---

### `GET /payments/history`

Get the user's payment transaction history.

**Auth required:** Yes

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "uuid",
        "pack_name": "standard",
        "amount_cents": 999,
        "currency": "usd",
        "credits_purchased": 150,
        "status": "completed",
        "created_at": "2026-05-31T10:00:00Z"
      }
    ]
  }
}
```

---

### `GET /payments/credits`

Get the current credit balance and ledger summary.

**Auth required:** Yes

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "balance": 44,
    "total_purchased": 200,
    "total_used": 156,
    "recent_transactions": []
  }
}
```

---

## 7. Stripe Webhook (`/webhooks`)

---

### `POST /webhooks/stripe`

Receive and process Stripe webhook events.

**Auth required:** No (Stripe signature verification instead)

**Headers required:**
- `stripe-signature`: Stripe webhook signature header

**Handled Events:**

| Event | Action |
|---|---|
| `checkout.session.completed` | Mark transaction as `completed`, add credits to ledger |
| `payment_intent.payment_failed` | Mark transaction as `failed` |
| `charge.refunded` | Mark transaction as `refunded`, deduct credits from ledger |

**Response `200`:**
```json
{ "received": true }
```

> ⚠️ Always return `200` to Stripe even on internal errors — log the error separately. Stripe retries on non-200 responses, which can cause duplicate credit additions.

---

## 8. User Profile Routes (`/users`)

---

### `PATCH /users/me`

Update the authenticated user's profile.

**Auth required:** Yes

**Request Body (all fields optional):**
```json
{
  "name": "Arjun K Nair",
  "avatar_url": "https://..."
}
```

**Response `200`:** Updated user object.

---

### `POST /users/me/change-password`

Change the user's password.

**Auth required:** Yes

**Request Body:**
```json
{
  "current_password": "OldPass123!",
  "new_password": "NewPass456!"
}
```

---

## 9. Error Code Reference

| Code | HTTP Status | Description |
|---|---|---|
| `EMAIL_ALREADY_EXISTS` | 409 | Email is already registered |
| `INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `ACCOUNT_INACTIVE` | 401 | Account has been deactivated |
| `INVALID_REFRESH_TOKEN` | 401 | Refresh token is invalid or revoked |
| `TOKEN_EXPIRED` | 401 | Token has expired |
| `INSUFFICIENT_CREDITS` | 402 | Not enough credits |
| `CHART_NOT_FOUND` | 404 | Birth chart not found |
| `PLACE_NOT_FOUND` | 400 | Could not geocode the given place |
| `INVALID_DATE` | 400 | Date of birth is invalid |
| `INVALID_TIME` | 400 | Time of birth is invalid |
| `AI_SERVICE_UNAVAILABLE` | 503 | AI provider returned an error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `FORBIDDEN` | 403 | Resource does not belong to user |
| `STRIPE_SIGNATURE_INVALID` | 400 | Webhook signature mismatch |
| `PACK_NOT_FOUND` | 400 | Unknown credit pack name |

---

## 10. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| API1 | OAuth (Google/Apple) endpoints in v1 | Yes / No | 🟡 Pending |
| API2 | Async AI calls (return job ID, poll for result) | Yes / No | 🟡 Pending |
| API3 | Webhook endpoint path | `/webhooks/stripe` (current) / `/stripe/webhook` | 🟡 Pending |
| API4 | Geocoding provider | Google / OpenCage / Nominatim | 🟡 Pending |
| API5 | Admin API routes | Separate `/admin/` prefix | 🟡 Pending |

---

*This document is a living specification. Finalized endpoints will be marked ✅.*
