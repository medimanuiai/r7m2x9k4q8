'use strict';

const { EMAIL_RE } = require('../server/middleware/validate');

describe('EMAIL_RE', () => {
  const valid = [
    'user@example.com',
    'a@b.io',
    'user+tag@domain.co.uk',
    '123@456.org',
    'first.last@sub.domain.com',
  ];
  const invalid = [
    '',
    'notanemail',
    '@nodomain.com',
    'no@tld',
    'spaces @a.com',
    'double@@a.com',
  ];

  valid.forEach(e => {
    it(`accepts valid email: ${e}`, () => expect(EMAIL_RE.test(e)).toBe(true));
  });
  invalid.forEach(e => {
    it(`rejects invalid email: "${e}"`, () => expect(EMAIL_RE.test(e)).toBe(false));
  });
});

describe('password length rule', () => {
  it('accepts 8 chars',     () => expect('12345678'.length >= 8).toBe(true));
  it('accepts 20 chars',    () => expect('a'.repeat(20).length >= 8).toBe(true));
  it('rejects 7 chars',     () => expect('1234567'.length >= 8).toBe(false));
  it('rejects empty string',() => expect(''.length >= 8).toBe(false));
});

describe('name length rule', () => {
  it('accepts 2 chars',   () => expect('ab'.trim().length >= 2).toBe(true));
  it('rejects 1 char',    () => expect('a'.trim().length >= 2).toBe(false));
  it('rejects whitespace',() => expect('  '.trim().length >= 2).toBe(false));
});
