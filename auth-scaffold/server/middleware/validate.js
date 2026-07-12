'use strict';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateLogin(req, res, next) {
  const { email = '', password = '' } = req.body;

  if (!EMAIL_RE.test(email.trim())) {
    return res.render('login', {
      error: 'Please enter a valid email address.',
      success: null,
      fields: { email },
    });
  }
  if (!password) {
    return res.render('login', {
      error: 'Password is required.',
      success: null,
      fields: { email },
    });
  }
  next();
}

function validateRegister(req, res, next) {
  const { name = '', email = '', password = '', confirmPassword = '' } = req.body;

  if (name.trim().length < 2) {
    return res.render('register', {
      error: 'Name must be at least 2 characters.',
      success: null,
      fields: { name, email },
    });
  }
  if (!EMAIL_RE.test(email.trim())) {
    return res.render('register', {
      error: 'Please enter a valid email address.',
      success: null,
      fields: { name, email },
    });
  }
  if (password.length < 8) {
    return res.render('register', {
      error: 'Password must be at least 8 characters.',
      success: null,
      fields: { name, email },
    });
  }
  if (password !== confirmPassword) {
    return res.render('register', {
      error: 'Passwords do not match.',
      success: null,
      fields: { name, email },
    });
  }
  next();
}

function validateForgot(req, res, next) {
  const { email = '' } = req.body;

  if (!EMAIL_RE.test(email.trim())) {
    return res.render('forgot-password', {
      error: 'Please enter a valid email address.',
      success: null,
      fields: { email },
    });
  }
  next();
}

module.exports = { validateLogin, validateRegister, validateForgot, EMAIL_RE };
