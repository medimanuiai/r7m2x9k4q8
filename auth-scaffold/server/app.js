'use strict';

// Load .env when present (dotenv is optional – skip if not installed)
try { require('dotenv').config({ path: require('path').join(__dirname, '../.env') }); } catch {}

const express      = require('express');
const path         = require('path');
const cookieParser = require('cookie-parser');
const { rateLimiter } = require('./middleware/rateLimiter');
const authRoutes   = require('./routes/auth');
const indexRoutes  = require('./routes/index');

const app  = express();
const PORT = process.env.PORT || 3000;

// Seed in-memory userStore from server/data/accounts.json when running the dev server.
async function seedAccountsIfNeeded() {
  try {
    const userStore = require('./store/userStore');
    const bcrypt = require('bcrypt');
    const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12', 10);
    const fs = require('fs').promises;
    const dataPath = require('path').join(__dirname, 'data', 'accounts.json');
    const txt = await fs.readFile(dataPath, 'utf8').catch(() => null);
    if (!txt) return;
    let accounts = [];
    try { accounts = JSON.parse(txt); } catch { accounts = []; }
    for (const acc of accounts) {
      const email = (acc.email || '').toString().trim().toLowerCase();
      if (!email) continue;
      const existing = await userStore.findByEmail(email);
      if (existing) continue;
      const password = acc.password || '';
      const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
      await userStore.create({ name: acc.name || 'User', email, passwordHash });
    }
  } catch (e) {
    // Non-fatal for dev
    console.error('seedAccountsIfNeeded error:', e.message);
  }
}

// ── View engine ─────────────────────────────────────────────────
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../ejs-variant/views'));

// ── Static assets ────────────────────────────────────────────────
app.use(express.static(path.join(__dirname, '../ejs-variant/public')));

// ── Body parsing ─────────────────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// ── Rate limiting on auth routes ──────────────────────────────────
app.use('/login',           rateLimiter);
app.use('/register',        rateLimiter);
app.use('/forgot-password', rateLimiter);

// ── Routes ───────────────────────────────────────────────────────
app.use('/', indexRoutes);
app.use('/', authRoutes);

// ── 404 ──────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).render('login', {
    error: 'Page not found.',
    success: null,
    fields: {},
  });
});

// ── Global error handler ─────────────────────────────────────────
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  if (process.env.NODE_ENV !== 'production') console.error(err.stack);
  res.status(500).render('login', {
    error: 'Something went wrong. Please try again.',
    success: null,
    fields: {},
  });
});

// ── Start only when run directly (not required by tests) ─────────
if (require.main === module) {
  // Seed accounts (dev) then start server
  (async () => {
    await seedAccountsIfNeeded();
    app.listen(PORT, () =>
      console.log(`[jyothishyam] Server running → http://localhost:${PORT}/login`)
    );
  })();
}

module.exports = app;
