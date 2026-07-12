# Jyothishyam — Credit & Payment System Specification

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Modules:** `backend/credit_manager.py`, `backend/routes/payments.py`, `backend/routes/webhooks.py`

---

## 1. Overview

The Credit & Payment system manages:
- User credit balances (virtual currency for AI actions)
- Credit deduction and logging for every AI operation
- Stripe-based one-time purchases of credit packs
- Webhook processing to confirm payments and top up balances
- Transaction history and audit trail

**Design Principle:** The `credit_ledger` table is the **single source of truth**. The balance is always computed from the ledger — it is never stored as a separate column on the `users` table.

---

## 2. Credit Pack Catalog

| Pack ID | Display Name | Price (USD) | Credits | Cost/Credit | Stripe Price ID |
|---|---|---|---|---|---|
| `starter` | Starter Pack | $4.99 | 50 | $0.10 | `price_starter_xxx` |
| `standard` | Standard Pack | $9.99 | 150 | $0.067 | `price_standard_xxx` |
| `pro` | Pro Pack | $19.99 | 400 | $0.05 | `price_pro_xxx` |

> Stripe Price IDs are configured via environment variables, not hardcoded.

---

## 3. Credit Action Costs

| Action | `question_type` | Credits Charged |
|---|---|---|
| General AI question | `general` | 1 |
| Daily prediction | `daily` | 1 |
| Weekly prediction | `weekly` | 2 |
| Monthly prediction | `monthly` | 3 |
| Full horoscope reading | `horoscope` | 10 |
| Compatibility check | `compatibility` | 5 |
| Admin grant / sign-up bonus | — | Variable (positive, free) |
| Refund | — | Variable (positive) |

---

## 4. `credit_manager.py`

### 4.1 Function: `get_balance`

**Purpose:** Return the current credit balance for a user.

**Signature:**
```python
async def get_balance(user_id: UUID, db: AsyncSession) -> int
```

**Implementation:**
```sql
SELECT COALESCE(SUM(credits_delta), 0)
FROM credit_ledger
WHERE user_id = :user_id
```

**Rules:**
- Returns `0` if no ledger entries exist (new user with no purchase or bonus yet).
- Always returns an integer (never negative by design).

---

### 4.2 Function: `check_sufficient_credits`

**Purpose:** Verify the user has enough credits before an AI action.

**Signature:**
```python
async def check_sufficient_credits(
    user_id: UUID,
    required: int,
    db: AsyncSession
) -> bool
```

**Returns:** `True` if balance ≥ required, `False` otherwise.

---

### 4.3 Function: `deduct_credits`

**Purpose:** Deduct credits for a completed AI action and log to ledger.

**Signature:**
```python
async def deduct_credits(
    user_id: UUID,
    amount: int,
    reason: str,
    reference_id: UUID | None,
    reference_type: str | None,
    db: AsyncSession
) -> CreditLedgerEntry
```

**Process:**
1. Get current balance → `current_balance`.
2. Assert `current_balance >= amount` (double-check, even if pre-checked).
3. Compute `balance_after = current_balance - amount`.
4. Insert ledger row:
   ```json
   {
     "entry_type": "debit",
     "credits_delta": -amount,
     "balance_after": balance_after,
     "reason": reason,
     "reference_id": reference_id,
     "reference_type": reference_type
   }
   ```
5. Return the created ledger entry.

**Error:** Raises `InsufficientCreditsError` if balance < amount (safety net).

---

### 4.4 Function: `add_credits`

**Purpose:** Add credits to a user's account (purchase or admin grant).

**Signature:**
```python
async def add_credits(
    user_id: UUID,
    amount: int,
    reason: str,
    reference_id: UUID | None,
    reference_type: str | None,
    db: AsyncSession
) -> CreditLedgerEntry
```

**Process:**
1. Get current balance → `current_balance`.
2. Compute `balance_after = current_balance + amount`.
3. Insert ledger row:
   ```json
   {
     "entry_type": "credit",
     "credits_delta": amount,
     "balance_after": balance_after,
     "reason": reason,
     "reference_id": reference_id,
     "reference_type": reference_type
   }
   ```
4. Return the created ledger entry.

---

### 4.5 Function: `get_ledger`

**Purpose:** Retrieve paginated ledger history for a user.

**Signature:**
```python
async def get_ledger(
    user_id: UUID,
    page: int = 1,
    per_page: int = 20,
    db: AsyncSession
) -> LedgerPage
```

---

## 5. Payment Flow (Stripe Checkout)

### 5.1 Full Purchase Flow

```
User clicks "Buy Standard Pack"
        ↓
Frontend → POST /api/v1/payments/checkout { "pack": "standard" }
        ↓
Backend: Validate pack name → look up pack catalog
Backend: Create Stripe Checkout Session
  - mode: "payment"
  - line_items: [{ price: STRIPE_PRICE_ID_STANDARD, quantity: 1 }]
  - success_url: "{FRONTEND_URL}/payments/success?session_id={CHECKOUT_SESSION_ID}"
  - cancel_url: "{FRONTEND_URL}/payments/cancel"
  - metadata: { user_id, pack, credits }
  - customer_email: user.email
        ↓
Backend: Create transactions row with status = "pending"
Backend: Return { checkout_url, session_id } to frontend
        ↓
Frontend: Redirect to Stripe Checkout URL
        ↓
User completes payment on Stripe
        ↓
Stripe: POST to /api/v1/webhooks/stripe with event "checkout.session.completed"
        ↓
Backend webhook handler:
  1. Verify Stripe signature
  2. Extract session metadata: user_id, pack, credits
  3. Find transaction by stripe_session_id
  4. Update transaction status → "completed"
  5. Call add_credits(user_id, credits, reason="purchase", reference_id=transaction.id)
  6. Return 200 OK
        ↓
User lands on /payments/success page
Frontend: GET /api/v1/payments/credits → show updated balance
```

---

### 5.2 Stripe Checkout Session Parameters

```python
stripe.checkout.Session.create(
    mode="payment",
    payment_method_types=["card"],
    line_items=[{
        "price": pack_config["stripe_price_id"],
        "quantity": 1,
    }],
    success_url=f"{settings.FRONTEND_URL}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
    cancel_url=f"{settings.FRONTEND_URL}/payments/cancel",
    customer_email=user.email,
    metadata={
        "user_id": str(user.id),
        "pack": pack_name,
        "credits": str(pack_config["credits"]),
        "internal_transaction_id": str(transaction.id),
    },
    expires_at=int(time.time()) + 1800,  # 30 min expiry
)
```

---

## 6. Stripe Webhook Handler

### 6.1 Event: `checkout.session.completed`

```python
session = event["data"]["object"]
user_id = UUID(session["metadata"]["user_id"])
credits = int(session["metadata"]["credits"])
transaction_id = UUID(session["metadata"]["internal_transaction_id"])

# Update transaction
await update_transaction_status(transaction_id, "completed", session["payment_intent"])

# Add credits
await add_credits(
    user_id=user_id,
    amount=credits,
    reason="purchase",
    reference_id=transaction_id,
    reference_type="transaction",
    db=db
)
```

### 6.2 Event: `payment_intent.payment_failed`

```python
# Find transaction by payment_intent_id and mark as "failed"
# Do NOT deduct or add credits
# Log the failure for monitoring
```

### 6.3 Event: `charge.refunded`

```python
# Find transaction by payment_intent_id
# Mark transaction status as "refunded"
# Deduct the credits that were previously added:
await deduct_credits(
    user_id=user_id,
    amount=credits,
    reason="refund",
    reference_id=transaction_id,
    reference_type="transaction",
    db=db
)
```

### 6.4 Webhook Security

```python
# Always verify Stripe signature before processing
try:
    event = stripe.Webhook.construct_event(
        payload=raw_body,
        sig_header=stripe_signature_header,
        secret=settings.STRIPE_WEBHOOK_SECRET
    )
except stripe.error.SignatureVerificationError:
    raise HTTPException(status_code=400, detail="Invalid Stripe signature")
```

> ⚠️ **CRITICAL:** Always return HTTP `200` to Stripe even if internal processing fails (log the error). If you return non-200, Stripe will retry the webhook up to 72 hours, potentially causing duplicate credit additions on retry success.

### 6.5 Idempotency

Webhook handlers must be idempotent — safe to call multiple times with the same event:
- Check if `stripe_session_id` already has status `completed` before processing.
- If already processed, return `200` silently.

---

## 7. Sign-Up Bonus

New users receive a welcome credit bonus to try the platform.

- **Amount:** 5 credits (configurable via `SIGNUP_BONUS_CREDITS` env var)
- **Trigger:** On successful `POST /auth/register`
- **Ledger reason:** `signup_bonus`

```python
await add_credits(
    user_id=new_user.id,
    amount=settings.SIGNUP_BONUS_CREDITS,
    reason="signup_bonus",
    reference_id=None,
    reference_type=None,
    db=db
)
```

---

## 8. Admin Credit Management

Admins can manually grant or deduct credits via admin-only endpoints (Phase 2):

- `POST /admin/users/{user_id}/credits/grant` — Add credits (e.g., compensation, contest)
- `POST /admin/users/{user_id}/credits/deduct` — Remove credits (e.g., abuse)
- `GET /admin/users/{user_id}/ledger` — Full ledger view

**Ledger reason:** `admin_grant` or `admin_deduct` with a mandatory `note` field.

---

## 9. Credit Balance Widget — Frontend Data Contract

The `GET /payments/credits` endpoint provides all data needed for the frontend credit widget:

```json
{
  "balance": 44,
  "total_purchased": 200,
  "total_used": 156,
  "recent_transactions": [
    {
      "type": "debit",
      "amount": 1,
      "reason": "ai_question",
      "date": "2026-05-31T10:00:00Z"
    },
    {
      "type": "credit",
      "amount": 150,
      "reason": "purchase",
      "pack": "standard",
      "date": "2026-05-30T08:00:00Z"
    }
  ]
}
```

---

## 10. Environment Variables

| Variable | Description | Example |
|---|---|---|
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | `whsec_...` |
| `STRIPE_PRICE_ID_STARTER` | Stripe Price ID for Starter Pack | `price_xxx` |
| `STRIPE_PRICE_ID_STANDARD` | Stripe Price ID for Standard Pack | `price_yyy` |
| `STRIPE_PRICE_ID_PRO` | Stripe Price ID for Pro Pack | `price_zzz` |
| `FRONTEND_URL` | Frontend base URL for redirect | `https://jyothishyam.com` |
| `SIGNUP_BONUS_CREDITS` | Credits given on registration | `5` |

---

## 11. Error Scenarios & Handling

| Scenario | Behavior |
|---|---|
| User has 0 credits, tries to ask AI | Return `402` with `INSUFFICIENT_CREDITS` error before AI call |
| Stripe payment fails | Transaction marked `failed`; no credits added |
| Webhook received but transaction not found | Log warning; attempt to recover from metadata; return 200 |
| Webhook duplicate event | Detect by `stripe_session_id` already `completed`; skip; return 200 |
| AI call fails after credit check | Credits are NOT deducted (only deduct after successful answer save) |
| Refund processed | Credits reversed via deduction ledger entry |

---

## 12. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| PAY1 | Subscription model in v2 | Yes (monthly) / No (one-time only) | 🟡 Pending |
| PAY2 | Credit expiry | No expiry (current) / 1 year | 🟡 Pending |
| PAY3 | Discount/promo codes | Phase 1 / Phase 2 | 🟡 Pending |
| PAY4 | Invoice emails | Stripe-managed / Custom | 🟡 Pending |
| PAY5 | Multi-currency | USD only / Auto by region | 🟡 Pending |
| PAY6 | Refund policy | Manual admin / Automatic partial | 🟡 Pending |

---

*This document is a living specification. Sections marked 🟡 are pending decisions.*
