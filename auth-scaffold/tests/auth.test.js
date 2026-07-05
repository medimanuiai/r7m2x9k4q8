'use strict';

process.env.NODE_ENV    = 'test';
process.env.BCRYPT_ROUNDS = '4'; // Fast bcrypt for tests

const request   = require('supertest');
const app       = require('../server/app');
const userStore = require('../server/store/userStore');

beforeEach(() => userStore._reset()); // Clear in-memory store between tests

// ── GET routes ────────────────────────────────────────────────────
describe('GET /login', () => {
  it('returns 200 and contains Login', async () => {
    const res = await request(app).get('/login');
    expect(res.status).toBe(200);
    expect(res.text).toContain('Login');
  });
});

describe('GET /register', () => {
  it('returns 200 and contains Create', async () => {
    const res = await request(app).get('/register');
    expect(res.status).toBe(200);
    expect(res.text).toMatch(/create|register/i);
  });
});

describe('GET /forgot-password', () => {
  it('returns 200', async () => {
    const res = await request(app).get('/forgot-password');
    expect(res.status).toBe(200);
  });
});

describe('GET /logout', () => {
  it('redirects to /login', async () => {
    const res = await request(app).get('/logout');
    expect(res.status).toBe(302);
    expect(res.headers.location).toContain('/login');
  });
  it('clears the auth cookie', async () => {
    const res = await request(app).get('/logout');
    const cookies = res.headers['set-cookie'] || [];
    const cleared = cookies.some(c => c.startsWith('auth_placeholder=;'));
    expect(cleared).toBe(true);
  });
});

// ── POST /register ────────────────────────────────────────────────
describe('POST /register – validation', () => {
  it('rejects name shorter than 2 chars', async () => {
    const res = await request(app).post('/register')
      .send({ name:'A', email:'a@b.com', password:'Pass1234!', confirmPassword:'Pass1234!' });
    expect(res.text).toMatch(/2 characters/i);
  });

  it('rejects invalid email', async () => {
    const res = await request(app).post('/register')
      .send({ name:'Alice', email:'bad', password:'Pass1234!', confirmPassword:'Pass1234!' });
    expect(res.text).toMatch(/valid email/i);
  });

  it('rejects short password', async () => {
    const res = await request(app).post('/register')
      .send({ name:'Alice', email:'a@b.com', password:'short', confirmPassword:'short' });
    expect(res.text).toMatch(/8 characters/i);
  });

  it('rejects password mismatch', async () => {
    const res = await request(app).post('/register')
      .send({ name:'Alice', email:'a@b.com', password:'Pass1234!', confirmPassword:'Different1!' });
    expect(res.text).toMatch(/do not match/i);
  });
});

describe('POST /register – success flow', () => {
  it('creates account and shows success message', async () => {
    const res = await request(app).post('/register')
      .send({ name:'Alice', email:'alice@test.com', password:'SecurePass1!', confirmPassword:'SecurePass1!' });
    expect(res.status).toBe(200);
    expect(res.text).toMatch(/created/i);
  });

  it('does not reveal if email already exists', async () => {
    const payload = { name:'Alice', email:'alice@test.com', password:'SecurePass1!', confirmPassword:'SecurePass1!' };
    await request(app).post('/register').send(payload);
    const res = await request(app).post('/register').send(payload);
    expect(res.text).not.toMatch(/already exists/i);
    expect(res.text).toMatch(/Could not create/i);
  });
});

// ── POST /login ───────────────────────────────────────────────────
describe('POST /login – validation', () => {
  it('rejects missing email', async () => {
    const res = await request(app).post('/login').send({ email:'', password:'pass' });
    expect(res.text).toMatch(/valid email/i);
  });

  it('rejects missing password', async () => {
    const res = await request(app).post('/login').send({ email:'a@b.com', password:'' });
    expect(res.text).toMatch(/required/i);
  });
});

describe('POST /login – auth', () => {
  const creds = { name:'Bob', email:'bob@test.com', password:'StrongPass1!', confirmPassword:'StrongPass1!' };

  beforeEach(async () => {
    await request(app).post('/register').send(creds);
  });

  it('rejects unknown user with generic message (no enumeration)', async () => {
    const res = await request(app).post('/login')
      .send({ email:'nobody@x.com', password:'StrongPass1!' });
    expect(res.text).toMatch(/Invalid email or password/i);
  });

  it('rejects wrong password with generic message', async () => {
    const res = await request(app).post('/login')
      .send({ email:'bob@test.com', password:'WrongPassword!' });
    expect(res.text).toMatch(/Invalid email or password/i);
  });

  it('accepts correct credentials and sets cookie', async () => {
    const res = await request(app).post('/login')
      .send({ email:'bob@test.com', password:'StrongPass1!' });
    expect(res.status).toBe(302);
    expect(res.headers.location).toContain('/dashboard');
    const cookies = res.headers['set-cookie'] || [];
    expect(cookies.some(c => c.startsWith('auth_placeholder='))).toBe(true);
  });
});

// ── POST /forgot-password ─────────────────────────────────────────
describe('POST /forgot-password', () => {
  it('always returns a success message (no enumeration)', async () => {
    const res = await request(app).post('/forgot-password')
      .send({ email:'anyone@x.com' });
    expect(res.text).toMatch(/reset link/i);
  });

  it('returns success even for unregistered email', async () => {
    const res = await request(app).post('/forgot-password')
      .send({ email:'notregistered@x.com' });
    expect(res.text).toMatch(/reset link/i);
  });

  it('rejects invalid email', async () => {
    const res = await request(app).post('/forgot-password')
      .send({ email:'invalid-email' });
    expect(res.text).toMatch(/valid email/i);
  });
});
