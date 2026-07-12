'use strict';

const { randomUUID } = require('crypto');

// ─────────────────────────────────────────────────────────────────────────────
// IN-MEMORY USER STORE  –  local dev only, resets on server restart
// ─────────────────────────────────────────────────────────────────────────────
/** @type {Map<string, {id:string,name:string,email:string,passwordHash:string,createdAt:Date}>} */
const _byId    = new Map();
const _byEmail = new Map();

const userStore = {
  async create({ name, email, passwordHash }) {
    const id   = randomUUID();
    const user = { id, name, email, passwordHash, createdAt: new Date() };
    _byId.set(id, user);
    _byEmail.set(email, user);
    return user;
  },

  async findByEmail(email) {
    return _byEmail.get(email) ?? null;
  },

  async findById(id) {
    return _byId.get(id) ?? null;
  },

  /** Exposed for test teardown only */
  _reset() {
    _byId.clear();
    _byEmail.clear();
  },
  /** Dev debug helper to inspect in-memory users (includes passwordHash) */
  _debugAll() {
    return Array.from(_byId.values());
  },
};

module.exports = userStore;

// ─────────────────────────────────────────────────────────────────────────────
// TODO: Mongoose / MongoDB  (uncomment + npm i mongoose)
// ─────────────────────────────────────────────────────────────────────────────
// const mongoose = require('mongoose');
// mongoose.connect(process.env.MONGODB_URI);
//
// const UserSchema = new mongoose.Schema({
//   name:         { type: String, required: true, minlength: 2, maxlength: 100, trim: true },
//   email:        { type: String, required: true, unique: true, lowercase: true, trim: true },
//   passwordHash: { type: String, required: true },
//   createdAt:    { type: Date, default: Date.now },
// });
// const User = mongoose.model('User', UserSchema);
//
// module.exports = {
//   create:      (data)  => User.create(data),
//   findByEmail: (email) => User.findOne({ email }),
//   findById:    (id)    => User.findById(id),
// };

// ─────────────────────────────────────────────────────────────────────────────
// TODO: Prisma / Postgres  (uncomment + npx prisma init)
// ─────────────────────────────────────────────────────────────────────────────
// Prisma schema (prisma/schema.prisma):
// model User {
//   id           String   @id @default(cuid())
//   name         String
//   email        String   @unique
//   passwordHash String
//   createdAt    DateTime @default(now())
// }
//
// const { PrismaClient } = require('@prisma/client');
// const prisma = new PrismaClient();
//
// module.exports = {
//   create:      (data)  => prisma.user.create({ data }),
//   findByEmail: (email) => prisma.user.findUnique({ where: { email } }),
//   findById:    (id)    => prisma.user.findUnique({ where: { id } }),
// };
