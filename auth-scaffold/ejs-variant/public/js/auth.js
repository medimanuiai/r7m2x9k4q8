/* jshint esversion:11 */
'use strict';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ── Dark mode ──────────────────────────────────────────────────────
(function initDarkMode() {
  const btn = document.getElementById('dark-toggle');
  if (!btn) return;

  const saved = localStorage.getItem('jy-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = saved === 'dark' || (!saved && prefersDark);

  if (isDark) applyDark(btn);

  btn.addEventListener('click', () => {
    const nowDark = document.documentElement.dataset.theme === 'dark';
    if (nowDark) {
      document.documentElement.dataset.theme = 'light';
      btn.textContent = '🌙';
      btn.setAttribute('aria-pressed', 'false');
      localStorage.setItem('jy-theme', 'light');
    } else {
      applyDark(btn);
      localStorage.setItem('jy-theme', 'dark');
    }
  });

  function applyDark(btn) {
    document.documentElement.dataset.theme = 'dark';
    btn.textContent = '☀️';
    btn.setAttribute('aria-pressed', 'true');
  }
})();

// ── Parallax silhouette on pointer move ───────────────────────────
(function initParallax() {
  const sil = document.querySelector('.auth-bg__silhouette');
  if (!sil) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.addEventListener('mousemove', (e) => {
    const x = (e.clientX / window.innerWidth  - 0.5) * 14;
    const y = (e.clientY / window.innerHeight - 0.5) * 10;
    sil.style.transform = `translate(${x}px, ${y}px)`;
  });
})();

// ── Helpers ────────────────────────────────────────────────────────
function setFieldError(id, msg) {
  const input = document.getElementById(id);
  const error = document.getElementById(`${id}-error`);
  const wrap  = document.getElementById(`${id}-wrap`) ||
                input?.closest('.field-input-wrap');
  if (input) {
    input.setAttribute('aria-invalid', 'true');
    if (wrap) wrap.classList.add('field-input-wrap--error');
  }
  if (error) error.textContent = msg;
}

function clearFieldError(id) {
  const input = document.getElementById(id);
  const error = document.getElementById(`${id}-error`);
  const wrap  = document.getElementById(`${id}-wrap`) ||
                input?.closest('.field-input-wrap');
  if (input) {
    input.removeAttribute('aria-invalid');
    if (wrap) wrap.classList.remove('field-input-wrap--error');
  }
  if (error) error.textContent = '';
}

function setSubmitLoading(formId) {
  const form    = document.getElementById(formId);
  if (!form) return;
  const btn     = form.querySelector('.btn-primary');
  const label   = btn?.querySelector('.btn-label');
  const spinner = btn?.querySelector('.btn-spinner');
  if (btn)     btn.disabled   = true;
  if (label)   label.hidden   = true;
  if (spinner) spinner.hidden = false;
}

// ── Login form ─────────────────────────────────────────────────────
(function initLoginForm() {
  const form = document.getElementById('login-form');
  if (!form) return;

  const emailEl    = document.getElementById('email');
  const passwordEl = document.getElementById('password');

  // Live blur validation
  emailEl?.addEventListener('blur', () => {
    if (emailEl.value && !EMAIL_RE.test(emailEl.value.trim())) {
      setFieldError('email', 'Please enter a valid email address.');
    } else {
      clearFieldError('email');
    }
  });

  form.addEventListener('submit', (e) => {
    let valid = true;
    clearFieldError('email');
    clearFieldError('password');

    if (!EMAIL_RE.test((emailEl?.value || '').trim())) {
      setFieldError('email', 'Please enter a valid email address.');
      valid = false;
    }
    if (!passwordEl?.value) {
      setFieldError('password', 'Password is required.');
      valid = false;
    }
    if (!valid) {
      e.preventDefault();
      form.querySelector('[aria-invalid="true"]')?.focus();
      return;
    }
    setSubmitLoading('login-form');
  });
})();

// ── Register form ──────────────────────────────────────────────────
(function initRegisterForm() {
  const form = document.getElementById('register-form');
  if (!form) return;

  const nameEl    = document.getElementById('name');
  const emailEl   = document.getElementById('email');
  const passEl    = document.getElementById('password');
  const confEl    = document.getElementById('confirmPassword');

  form.addEventListener('submit', (e) => {
    let valid = true;
    ['name','email','password','confirmPassword'].forEach(clearFieldError);

    if (!nameEl?.value.trim() || nameEl.value.trim().length < 2) {
      setFieldError('name', 'Name must be at least 2 characters.');
      valid = false;
    }
    if (!EMAIL_RE.test((emailEl?.value || '').trim())) {
      setFieldError('email', 'Please enter a valid email address.');
      valid = false;
    }
    if (!passEl?.value || passEl.value.length < 8) {
      setFieldError('password', 'Password must be at least 8 characters.');
      valid = false;
    }
    if (confEl?.value !== passEl?.value) {
      setFieldError('confirmPassword', 'Passwords do not match.');
      valid = false;
    }
    if (!valid) {
      e.preventDefault();
      form.querySelector('[aria-invalid="true"]')?.focus();
      return;
    }
    setSubmitLoading('register-form');
  });
})();

// ── Forgot-password form ───────────────────────────────────────────
(function initForgotForm() {
  const form = document.getElementById('forgot-form');
  if (!form) return;

  const emailEl = document.getElementById('email');

  form.addEventListener('submit', (e) => {
    clearFieldError('email');
    if (!EMAIL_RE.test((emailEl?.value || '').trim())) {
      setFieldError('email', 'Please enter a valid email address.');
      e.preventDefault();
      emailEl?.focus();
      return;
    }
    setSubmitLoading('forgot-form');
  });
})();
