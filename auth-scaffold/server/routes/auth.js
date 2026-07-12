'use strict';

const express   = require('express');
const bcrypt    = require('bcrypt');
const router    = express.Router();
const fs        = require('fs').promises;
const path      = require('path');
const { validateLogin, validateRegister, validateForgot } = require('../middleware/validate');
const authCheck = require('../middleware/authCheck');
const userStore = require('../store/userStore');

const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12', 10);

// ── GET /login ────────────────────────────────────────────────────
router.get('/login', (req, res) => {
  res.render('login', { error: null, success: null, fields: {} });
});

// ── POST /login ───────────────────────────────────────────────────
router.post('/login', validateLogin, async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await userStore.findByEmail(email.trim().toLowerCase());
    const match = user ? await bcrypt.compare(password, user.passwordHash) : false;

    // Generic message — never reveal whether the email exists
    if (!user || !match) {
      return res.render('login', {
        error: 'Invalid email or password.',
        success: null,
        fields: { email },
      });
    }

    // TODO: Replace with real session management or JWT
    // TODO: Replace with real session management or JWT
    res.cookie('auth_placeholder', Buffer.from(user.id).toString('base64'), {
      httpOnly: true,
      sameSite: 'strict',
      maxAge: 60 * 60 * 1000, // 1 h
      // TODO: secure: true  (enable in production behind HTTPS)
    });

    res.redirect('/dashboard');
  } catch (err) {
    console.error(err);
    res.render('login', {
      error: 'Something went wrong. Please try again.',
      success: null,
      fields: { email },
    });
  }
});

// ── GET /register ─────────────────────────────────────────────────
router.get('/register', (req, res) => {
  res.render('register', { error: null, success: null, fields: {} });
});

// ── POST /register ────────────────────────────────────────────────
router.post('/register', validateRegister, async (req, res) => {
  const { name, email, password } = req.body;
  try {
    const existing = await userStore.findByEmail(email.trim().toLowerCase());
    if (existing) {
      // Generic message — never reveal email existence
      return res.render('register', {
        error: 'Could not create account. Please check your details.',
        success: null,
        fields: { name, email },
      });
    }

    const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
    await userStore.create({
      name: name.trim(),
      email: email.trim().toLowerCase(),
      passwordHash,
    });

    // Temporary persistence: append account creation to server/data/accounts.json
    // NOTE: This stores the plain-text password for short-term local development only.
    // Remove this once a real database is in use.
    try {
      const dataDir = path.join(__dirname, '../data');
      await fs.mkdir(dataDir, { recursive: true });
      const filePath = path.join(dataDir, 'accounts.json');
      let accounts = [];
      try {
        const txt = await fs.readFile(filePath, 'utf8');
        accounts = JSON.parse(txt || '[]');
      } catch (e) {
        accounts = [];
      }
      accounts.push({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password: password,
        createdAt: new Date().toISOString(),
      });
      await fs.writeFile(filePath, JSON.stringify(accounts, null, 2), 'utf8');
    } catch (e) {
      console.error('Failed to persist account to JSON:', e);
    }

    res.render('register', {
      error: null,
      success: 'Account created! You can now log in.',
      fields: {},
    });
  } catch (err) {
    console.error(err);
    res.render('register', {
      error: 'Something went wrong. Please try again.',
      success: null,
      fields: { name, email },
    });
  }
});

// JSON API: POST /api/v1/auth/register
router.post('/api/v1/auth/register', validateRegister, async (req, res) => {
  const { name, email, password } = req.body;
  try {
    const existing = await userStore.findByEmail(email.trim().toLowerCase());
    if (existing) {
      return res.status(400).json({ error: { message: 'Could not create account. Please check your details.' } });
    }
    const passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
    const user = await userStore.create({ name: name.trim(), email: email.trim().toLowerCase(), passwordHash });

    // also append to accounts.json for dev convenience
    try {
      const fs2 = require('fs').promises;
      const path2 = require('path');
      const dataDir = path2.join(__dirname, '../data');
      await fs2.mkdir(dataDir, { recursive: true });
      const filePath = path2.join(dataDir, 'accounts.json');
      let accounts = [];
      try { accounts = JSON.parse(await fs2.readFile(filePath, 'utf8') || '[]'); } catch { accounts = []; }
      accounts.push({ name: user.name, email: user.email, password, createdAt: new Date().toISOString() });
      await fs2.writeFile(filePath, JSON.stringify(accounts, null, 2), 'utf8');
    } catch (e) { console.error('Failed to persist account to JSON:', e); }

    return res.json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: { message: 'Something went wrong. Please try again.' } });
  }
});

// ── GET /logout ───────────────────────────────────────────────────
router.get('/logout', (req, res) => {
  res.clearCookie('auth_placeholder');
  res.redirect('/login');
});

// ── GET /forgot-password ──────────────────────────────────────────
router.get('/forgot-password', (req, res) => {
  res.render('forgot-password', { error: null, success: null, fields: {} });
});

// ── POST /forgot-password ─────────────────────────────────────────
router.post('/forgot-password', validateForgot, async (req, res) => {
  // TODO: Generate secure reset token, store it, send email via nodemailer/SendGrid
  // Always return success to prevent email enumeration
  res.render('forgot-password', {
    error: null,
    success: 'If an account exists for that email, a reset link has been sent.',
    fields: {},
  });
});

// ── GET /dashboard (protected stub) ──────────────────────────────
router.get('/dashboard', authCheck, (req, res) => {
  const name = res.locals.user?.name || 'User';
  res.send(`
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Dashboard</title>
    <style>body{font-family:sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f0f4ff}</style>
    </head><body>
    <div style="text-align:center">
      <h1 style="color:#7c3aed">Welcome, ${name}! 🪐</h1>
      <p style="color:#6b7280">Your Jyothishyam dashboard is coming soon.</p>
      <a href="/logout" style="color:#7c3aed">Log out</a>
    </div></body></html>
  `);
});

// JSON API: POST /api/v1/auth/login
router.post('/api/v1/auth/login', validateLogin, async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await userStore.findByEmail(email.trim().toLowerCase());
    const match = user ? await bcrypt.compare(password, user.passwordHash) : false;
    if (!user || !match) {
      return res.status(401).json({ error: { message: 'Invalid email or password.' } });
    }
    res.cookie('auth_placeholder', Buffer.from(user.id).toString('base64'), {
      httpOnly: true,
      sameSite: 'strict',
      maxAge: 60 * 60 * 1000,
    });
    return res.json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: { message: 'Something went wrong. Please try again.' } });
  }
});
module.exports = router;
