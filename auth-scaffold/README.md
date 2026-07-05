# Jyothishyam – Auth Scaffold

Two frontend variants (React + Vite / Tailwind **and** EJS / vanilla CSS) backed by a shared
Express server with an in-memory user store for local dev.

---

## File Structure

```
auth-scaffold/
├── README.md
├── package.json               ← server deps + test scripts
├── jest.config.js
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
├── server/
│   ├── app.js                 ← Express entry
│   ├── routes/
│   │   ├── index.js
│   │   └── auth.js            ← all auth routes
│   ├── middleware/
│   │   ├── validate.js        ← server-side input validation
│   │   ├── rateLimiter.js     ← configurable rate-limit stub
│   │   └── authCheck.js       ← cookie auth guard
│   └── store/
│       └── userStore.js       ← in-memory store + commented Mongoose/Prisma
│
├── ejs-variant/               ← server-rendered + vanilla CSS
│   ├── views/
│   │   ├── login.ejs
│   │   ├── register.ejs
│   │   ├── forgot-password.ejs
│   │   └── partials/
│   │       └── _loginBackground.ejs
│   └── public/
│       ├── css/
│       │   ├── tokens.css
│       │   └── auth.css
│       ├── js/
│       │   └── auth.js
│       └── assets/
│           └── yoga-silhouette.svg
│
├── react-variant/             ← React + Vite + Tailwind CSS
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css          ← Tailwind + custom tokens
│       ├── assets/
│       │   └── yoga-silhouette.svg
│       └── components/
│           ├── LoginBackground.jsx
│           ├── DarkModeToggle.jsx
│           ├── LoginPage.jsx
│           ├── RegisterPage.jsx
│           └── ForgotPasswordPage.jsx
│
├── tokens/
│   └── design-tokens.json
│
└── tests/
    ├── auth.test.js
    └── validate.test.js
```

---

## Quickstart

### Option A – EJS + Express (server-rendered)

```bash
cd auth-scaffold
npm install
npm run dev
# http://localhost:3000/login
```

### Option B – React + Vite (SPA, proxies API to Express)

```bash
# Terminal 1 – start Express API
cd auth-scaffold
npm run dev

# Terminal 2 – start Vite dev server
cd auth-scaffold/react-variant
npm install
npm run dev
# http://localhost:5173
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in:

| Variable         | Default         | Note                                      |
|------------------|-----------------|-------------------------------------------|
| `PORT`           | `3000`          |                                           |
| `BCRYPT_ROUNDS`  | `12`            | Lower for tests (e.g. 4)                 |
| `SESSION_SECRET` | –               | **TODO**: set a long random string        |
| `MONGODB_URI`    | –               | **TODO**: uncomment Mongoose in userStore |
| `DATABASE_URL`   | –               | **TODO**: uncomment Prisma in userStore   |

---

## Running Tests

```bash
npm test              # run Jest + Supertest
npm run test:coverage # with coverage report
```

Target coverage for auth logic: **≥ 80 %** on `server/routes/auth.js` and `server/middleware/validate.js`.

---

## TODO – Production Security Checklist

- [ ] Replace in-memory store with MongoDB (Mongoose) or Postgres (Prisma)
- [ ] Implement real sessions (`express-session` + `connect-mongo`) or short-lived JWT + refresh tokens
- [ ] Add CSRF protection (`csurf` or double-submit cookie)
- [ ] Replace rate-limiter stub with Redis-backed `rate-limit-redis`
- [ ] Set `secure: true`, `sameSite: 'strict'`, `httpOnly: true` on all cookies
- [ ] Add email-verification flow after registration
- [ ] Implement OAuth2 social login (Google, Facebook, Twitter)
- [ ] Configure TLS / HTTPS in production
- [ ] Rotate and store all secrets in environment / vault (never commit to VCS)
- [ ] Add `helmet` for HTTP security headers
- [ ] Add `morgan` structured request logging

---

## Docker

```bash
docker-compose up --build
# App at http://localhost:3000
```

---

## Deployment Notes

- Set `NODE_ENV=production` — Express will disable stack traces in error responses.
- Place the app behind a reverse proxy (nginx / Caddy) that terminates TLS.
- Use a process manager (`pm2`) or container orchestration for restarts.
