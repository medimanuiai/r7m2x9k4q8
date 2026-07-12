# Jyothishyam — Authentication & Authorization Specification

**Version:** 0.1 (Draft)
**Last Updated:** 2026-05-31
**Status:** 🟡 In Review
**Module:** `backend/routes/auth.py`, `backend/auth/`
**Language:** Python 3.11+

---

## 1. Overview

Authentication is JWT-based with a short-lived access token and a long-lived refresh token. Passwords are hashed with bcrypt. All sensitive operations require a valid access token.

OAuth (Google / Apple) is architecturally supported but **not implemented in Phase 1**.

---

## 2. Token Architecture

### 2.1 Access Token (JWT)

| Property | Value |
|---|---|
| Format | JWT (JSON Web Token) |
| Algorithm | `HS256` |
| Expiry | 15 minutes |
| Signing secret | `JWT_SECRET_KEY` (env var, min 32 chars) |
| Payload claims | `sub` (user_id), `email`, `role`, `iat`, `exp`, `jti` |

**Sample Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "arjun@example.com",
  "role": "user",
  "iat": 1748685600,
  "exp": 1748686500,
  "jti": "unique-token-id-uuid"
}
```

### 2.2 Refresh Token

| Property | Value |
|---|---|
| Format | Opaque random token (32-byte URL-safe base64) |
| Expiry | 7 days |
| Storage (backend) | Hashed with bcrypt in `refresh_tokens` table |
| Storage (client) | httpOnly cookie (preferred) OR localStorage |
| Rotation | Each use of a refresh token issues a new one and revokes the old |

---

## 3. Password Policy

| Rule | Requirement |
|---|---|
| Minimum length | 8 characters |
| Maximum length | 128 characters |
| Uppercase | At least 1 |
| Lowercase | At least 1 |
| Digit | At least 1 |
| Special character | At least 1 (`!@#$%^&*()_+-=[]{}`) |
| Common passwords | Rejected (checked against top-1000 password list) |
| Hashing algorithm | bcrypt, cost factor 12 |

---

## 4. Auth Module Structure

```
backend/auth/
├── __init__.py
├── jwt_handler.py          ← JWT create, decode, validate
├── password_handler.py     ← bcrypt hash, verify, strength check
├── dependencies.py         ← FastAPI dependency: get_current_user
└── oauth.py                ← Google/Apple OAuth (stub for Phase 2)
```

---

## 5. `jwt_handler.py`

### 5.1 `create_access_token`

```python
def create_access_token(
    user_id: UUID,
    email: str,
    role: str
) -> str
```

**Process:**
1. Build payload with `sub`, `email`, `role`, `iat`, `exp`, `jti`.
2. Sign with `JWT_SECRET_KEY` using `HS256`.
3. Return encoded token string.

### 5.2 `decode_access_token`

```python
def decode_access_token(token: str) -> TokenPayload
```

**Process:**
1. Decode and verify JWT signature.
2. Verify `exp` claim (raises `TokenExpiredError` if expired).
3. Return `TokenPayload` Pydantic model.

**Raises:**
- `TokenExpiredError` — token has expired
- `InvalidTokenError` — signature invalid or malformed

### 5.3 `TokenPayload` (Pydantic model)

```python
class TokenPayload(BaseModel):
    sub: UUID       # user_id
    email: str
    role: str
    iat: int
    exp: int
    jti: str
```

---

## 6. `password_handler.py`

### 6.1 `hash_password`

```python
def hash_password(plain_password: str) -> str
```

Returns a bcrypt hash string. Cost factor: 12.

### 6.2 `verify_password`

```python
def verify_password(plain_password: str, hashed: str) -> bool
```

Returns `True` if password matches hash.

### 6.3 `check_password_strength`

```python
def check_password_strength(password: str) -> PasswordStrengthResult
```

```python
class PasswordStrengthResult(BaseModel):
    is_valid: bool
    errors: list[str]   # e.g., ["Must contain at least 1 uppercase letter"]
```

---

## 7. `dependencies.py` — FastAPI Auth Dependency

### 7.1 `get_current_user`

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User
```

**Process:**
1. Extract Bearer token from `Authorization` header.
2. Call `decode_access_token(token)`.
3. Fetch user from DB by `sub` (user_id).
4. Verify user is active (`is_active = True`).
5. Return `User` ORM model.

**Raises:**
- `HTTPException(401)` — missing token, invalid token, expired token
- `HTTPException(401)` — user not found
- `HTTPException(401)` — account inactive

### 7.2 `get_current_admin`

```python
async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User
```

**Raises:** `HTTPException(403)` if `current_user.role != "admin"`.

### 7.3 Usage in Routes

```python
@router.get("/charts")
async def list_charts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ...
```

---

## 8. Registration Flow

```
POST /auth/register
        ↓
1. Validate request body (Pydantic)
2. Check password strength → return 400 if weak
3. Normalize email (lowercase, strip whitespace)
4. Check if email exists in DB → return 409 if exists
5. Hash password (bcrypt, cost 12)
6. Create user row in DB (role="user", is_active=True)
7. Generate access_token + refresh_token
8. Store refresh_token hash in refresh_tokens table
9. Add signup bonus credits (credit_manager.add_credits)
10. Return user + tokens
```

---

## 9. Login Flow

```
POST /auth/login
        ↓
1. Validate request body
2. Normalize email
3. Fetch user by email → 401 if not found
4. Check is_active → 401 if inactive
5. Verify password (bcrypt) → 401 if mismatch
6. Generate new access_token + refresh_token
7. Store refresh_token hash (revoke old tokens for this user if rotating)
8. Return user + tokens + credit_balance
```

**Timing Attack Prevention:** Always run `verify_password` even if user not found (using a dummy hash) to ensure constant-time response.

---

## 10. Token Refresh Flow

```
POST /auth/refresh
        ↓
1. Receive refresh_token from body
2. Hash the received token
3. Look up matching unhashed record in refresh_tokens table
4. Check expires_at > now() → 401 if expired
5. Check revoked_at IS NULL → 401 if revoked
6. Fetch user by user_id
7. Generate new access_token
8. Generate new refresh_token (token rotation)
9. Revoke old refresh_token (set revoked_at)
10. Store new refresh_token hash
11. Return new access_token (+ optionally new refresh_token)
```

---

## 11. Logout Flow

```
POST /auth/logout
        ↓
1. Require Authorization header (valid access token)
2. Receive refresh_token in body
3. Look up refresh_token in DB
4. If found and belongs to current user → set revoked_at = NOW()
5. Return success
```

---

## 12. Security Measures

### 12.1 Brute Force Protection
- Rate limit `/auth/login` and `/auth/register`: max 10 requests/minute per IP.
- After 5 failed login attempts for the same email within 15 minutes: lock account for 15 minutes and notify user by email (Phase 2).

### 12.2 Refresh Token Security
- Refresh tokens stored as bcrypt hashes in DB — never raw.
- Implement **refresh token rotation**: every refresh issues a new token and revokes the old one.
- Detect token reuse: if a revoked refresh token is used, revoke ALL tokens for that user (potential theft scenario) — log a security alert.

### 12.3 JWT Security
- Short expiry (15 min) limits damage from stolen access tokens.
- `jti` claim allows future token revocation if needed.
- Secret key must be ≥ 32 random bytes, stored only in env vars.

### 12.4 Password Security
- Never log passwords in any form (plain or hash).
- Never return password hash in any API response.
- Never compare passwords with `==` — always use `bcrypt.verify`.

### 12.5 Transport Security
- All endpoints must use HTTPS in production.
- HSTS header enforced.
- `Secure` + `HttpOnly` + `SameSite=Strict` cookie flags for refresh token cookie.

---

## 13. Environment Variables

| Variable | Description | Example |
|---|---|---|
| `JWT_SECRET_KEY` | JWT signing secret (min 32 chars) | `supersecretrandomstring...` |
| `JWT_ALGORITHM` | Algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `SIGNUP_BONUS_CREDITS` | Credits on registration | `5` |

---

## 14. Error Reference

| Code | HTTP | Description |
|---|---|---|
| `EMAIL_ALREADY_EXISTS` | 409 | Email already registered |
| `WEAK_PASSWORD` | 400 | Password doesn't meet policy |
| `INVALID_CREDENTIALS` | 401 | Wrong email/password |
| `ACCOUNT_INACTIVE` | 401 | Account deactivated |
| `TOKEN_EXPIRED` | 401 | JWT access token expired |
| `INVALID_REFRESH_TOKEN` | 401 | Refresh token invalid/revoked |
| `TOKEN_REUSE_DETECTED` | 401 | Revoked refresh token was used (security alert) |
| `FORBIDDEN` | 403 | Role insufficient for this action |

---

## 15. Open Decisions

| # | Decision | Options | Status |
|---|---|---|---|
| AUTH1 | Refresh token storage on client | httpOnly cookie / localStorage | 🟡 Pending |
| AUTH2 | Google OAuth in Phase 1 | Yes / No | 🟡 Pending |
| AUTH3 | Email verification required | Yes (send email) / No (skip in v1) | 🟡 Pending |
| AUTH4 | "Forgot Password" in Phase 1 | Yes (email reset) / No | 🟡 Pending |
| AUTH5 | Account lockout on brute force | Phase 1 / Phase 2 | 🟡 Pending |
| AUTH6 | JWT algorithm | HS256 (current) / RS256 (asymmetric) | 🟡 Pending |

---

*This document is a living specification. Sections marked 🟡 are pending decisions.*
