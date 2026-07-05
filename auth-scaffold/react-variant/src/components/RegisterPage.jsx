import { useState } from 'react';
import LoginBackground from './LoginBackground.jsx';
import DarkModeToggle  from './DarkModeToggle.jsx';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function RegisterPage({ navigate }) {
  const [form,     setForm]     = useState({ name:'', email:'', password:'', confirm:'' });
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);
  const [success,  setSuccess]  = useState(null);
  const [fieldErr, setFieldErr] = useState({});
  const [darkMode, setDarkMode] = useState(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  const set = (k) => (e) => {
    setForm(f => ({ ...f, [k]: e.target.value }));
    setFieldErr(fe => ({ ...fe, [k]: undefined }));
  };

  const validate = () => {
    const e = {};
    if (form.name.trim().length < 2)      e.name     = 'Name must be at least 2 characters.';
    if (!EMAIL_RE.test(form.email.trim())) e.email    = 'Please enter a valid email address.';
    if (form.password.length < 8)          e.password = 'Password must be at least 8 characters.';
    if (form.confirm !== form.password)    e.confirm  = 'Passwords do not match.';
    return e;
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    setError(null); setSuccess(null);
    const errs = validate();
    if (Object.keys(errs).length) { setFieldErr(errs); return; }
    setFieldErr({});
    setLoading(true);
    try {
      const res = await fetch('/api/v1/auth/register', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({
          name: form.name.trim(),
          email: form.email.trim().toLowerCase(),
          password: form.password,
          confirmPassword: form.confirm,
        }),
      });
      const payload = await res.json();
      if (!res.ok) { setError(payload?.error?.message || 'Could not create account.'); return; }
      setSuccess('Account created! Redirecting to login…');
      setTimeout(() => navigate('login'), 1500);
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const inputBase = (k) =>
    `field-underline w-full py-3 pr-2 text-base text-gray-900 dark:text-gray-100 dark:bg-transparent` +
    (fieldErr[k] ? ' border-red-500' : '');

  const wrapBase = (k) =>
    `relative flex items-center border-b-[1.5px] transition-colors` +
    (fieldErr[k]
      ? ' border-red-500'
      : ' border-gray-200 dark:border-gray-600 focus-within:border-violet-600 dark:focus-within:border-violet-400');

  return (
    <div className="min-h-screen relative font-sans" data-theme={darkMode ? 'dark' : 'light'}>
      <LoginBackground darkMode={darkMode} />
      <main className="relative z-10 min-h-screen flex items-center justify-center p-6" role="main">
        <div className="w-full max-w-[420px] bg-white dark:bg-[#1e1b2e] rounded-[18px]
                        shadow-card px-8 py-10 text-center"
             role="region" aria-labelledby="reg-title">

          <div className="w-14 h-14 mx-auto mb-4 rounded-full flex items-center justify-center
                          text-2xl shadow-lg"
               style={{ background:'linear-gradient(135deg,#43e8d8,#c471ed)' }} aria-hidden="true">🌟</div>

          <h1 id="reg-title" className="text-[1.75rem] font-bold mb-6 tracking-tight
                                        text-gray-900 dark:text-gray-100">Create Account</h1>

          {error   && <div className="mb-4 px-4 py-3 rounded-lg text-sm text-left bg-red-50 text-red-800 border border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800" role="alert" aria-live="polite">{error}</div>}
          {success && <div className="mb-4 px-4 py-3 rounded-lg text-sm text-left bg-green-50 text-green-800 border border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800" role="status" aria-live="polite">{success}</div>}

          <form onSubmit={handleSubmit} noValidate aria-label="Registration form" className="text-left">
            {/* Name */}
            <div className="mb-5">
              <label htmlFor="name" className="block text-sm font-medium text-gray-500 mb-0.5">Full Name</label>
              <div className={wrapBase('name')}>
                <span className="absolute left-0 text-gray-400 pointer-events-none flex items-center" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                </span>
                <input id="name" className={inputBase('name')} value={form.name} onChange={set('name')} placeholder="Your full name" autoComplete="name" required aria-required="true" aria-invalid={!!fieldErr.name} aria-describedby={fieldErr.name ? 'name-error' : undefined} minLength="2" maxLength="100" />
              </div>
              {fieldErr.name && <span id="name-error" className="text-xs text-red-600 mt-1 block" role="alert">{fieldErr.name}</span>}
            </div>

            {/* Email */}
            <div className="mb-5">
              <label htmlFor="reg-email" className="block text-sm font-medium text-gray-500 mb-0.5">Email</label>
              <div className={wrapBase('email')}>
                <span className="absolute left-0 text-gray-400 pointer-events-none flex items-center" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                </span>
                <input id="reg-email" type="email" className={inputBase('email')} value={form.email} onChange={set('email')} placeholder="you@example.com" autoComplete="email" required aria-required="true" aria-invalid={!!fieldErr.email} aria-describedby={fieldErr.email ? 'email-error' : undefined} />
              </div>
              {fieldErr.email && <span id="email-error" className="text-xs text-red-600 mt-1 block" role="alert">{fieldErr.email}</span>}
            </div>

            {/* Password */}
            <div className="mb-5">
              <label htmlFor="reg-password" className="block text-sm font-medium text-gray-500 mb-0.5">Password</label>
              <div className={wrapBase('password')}>
                <span className="absolute left-0 text-gray-400 pointer-events-none flex items-center" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </span>
                <input id="reg-password" type="password" className={inputBase('password')} value={form.password} onChange={set('password')} placeholder="Min 8 characters" autoComplete="new-password" required aria-required="true" aria-invalid={!!fieldErr.password} aria-describedby={fieldErr.password ? 'pass-error' : 'pass-hint'} minLength="8" />
              </div>
              {fieldErr.password && <span id="pass-error" className="text-xs text-red-600 mt-1 block" role="alert">{fieldErr.password}</span>}
              {!fieldErr.password && <span id="pass-hint" className="text-[0.7rem] text-gray-400 mt-1 block">Use 8+ chars with uppercase, number &amp; symbol.</span>}
            </div>

            {/* Confirm */}
            <div className="mb-6">
              <label htmlFor="confirm" className="block text-sm font-medium text-gray-500 mb-0.5">Confirm Password</label>
              <div className={wrapBase('confirm')}>
                <span className="absolute left-0 text-gray-400 pointer-events-none flex items-center" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
                </span>
                <input id="confirm" type="password" className={inputBase('confirm')} value={form.confirm} onChange={set('confirm')} placeholder="Repeat your password" autoComplete="new-password" required aria-required="true" aria-invalid={!!fieldErr.confirm} aria-describedby={fieldErr.confirm ? 'confirm-error' : undefined} />
              </div>
              {fieldErr.confirm && <span id="confirm-error" className="text-xs text-red-600 mt-1 block" role="alert">{fieldErr.confirm}</span>}
            </div>

            <button type="submit" disabled={loading}
                    className="btn-grad w-full h-12 rounded-full text-white font-bold text-sm tracking-widest
                               flex items-center justify-center gap-2
                               focus-visible:outline-3 focus-visible:outline-violet-600 focus-visible:outline-offset-2">
              {loading ? <span className="btn-spinner" aria-hidden="true" /> : 'CREATE ACCOUNT'}
            </button>
          </form>

          <div className="border-t border-gray-200 dark:border-gray-700 mt-6 pt-5
                          text-sm text-gray-500 dark:text-gray-400">
            Already have an account?
            <button type="button" onClick={() => navigate('login')}
                    className="block mx-auto mt-2 font-bold tracking-wide text-gray-900 dark:text-gray-100
                               hover:text-violet-600 focus-visible:outline-2 focus-visible:outline-violet-600 rounded">
              LOG IN
            </button>
          </div>
        </div>
      </main>
      <DarkModeToggle darkMode={darkMode} onToggle={() => setDarkMode(d => !d)} />
    </div>
  );
}
