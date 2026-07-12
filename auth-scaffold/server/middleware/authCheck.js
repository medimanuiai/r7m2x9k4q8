'use strict';

const userStore = require('../store/userStore');

/**
 * Checks for a valid auth_placeholder cookie.
 * TODO: Replace with real JWT verification or express-session check.
 */
async function authCheck(req, res, next) {
  const token = req.cookies?.auth_placeholder;
  if (!token) return res.redirect('/login');

  try {
    const id   = Buffer.from(token, 'base64').toString('utf8');
    const user = await userStore.findById(id);
    if (!user) return res.redirect('/login');

    res.locals.user = { id: user.id, name: user.name, email: user.email };
    next();
  } catch {
    res.redirect('/login');
  }
}

module.exports = authCheck;
