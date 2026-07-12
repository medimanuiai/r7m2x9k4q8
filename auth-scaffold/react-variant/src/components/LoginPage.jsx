import { useState, useCallback } from 'react';
import LoginBackground from './LoginBackground.jsx';
import DarkModeToggle  from './DarkModeToggle.jsx';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ── Icon helpers ───────────────────────────────────────────────────
const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
       aria-hidden="true">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);
const LockIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
       aria-hidden="true">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);

function Field({ id, label, type = 'text', value, onChange, placeholder, autoComplete, error }) {
  return (
    <div className="mb-5">
      <label htmlFor={id} className="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-0.5">
        {label}
      </label>
      <div className={`relative flex items-center border-b-[1.5px] transition-colors
        ${error ? 'border-red-500' : 'border-gray-200 dark:border-gray-600 focus-within:border-violet-600 dark:focus-within:border-violet-400'}`}>
        <span className="absolute left-0 text-gray-400 dark:text-gray-500 flex items-center
                         peer-focus:text-violet-600 pointer-events-none">
          {type === 'password' ? <LockIcon /> : <UserIcon />}
        </span>
        <input
          id={id}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          required
          aria-required="true"
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          className="field-underline w-full py-3 pr-2 text-base text-gray-900 dark:text-gray-100
                     dark:bg-transparent peer focus-visible:ring-0"
        />
      </div>
      {error && (
        <span id={`${id}-error`} className="block text-xs text-red-600 mt-1" role="alert">{error}</span>
      )}
    </div>
  );
}

export default function LoginPage({ navigate }) {
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);
  const [fieldErr, setFieldErr] = useState({});
  const [darkMode, setDarkMode] = useState(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  const validate = useCallback(() => {
    const e = {};
    if (!EMAIL_RE.test(email.trim()))  e.email    = 'Please enter a valid email address.';
    if (!password)                      e.password = 'Password is required.';
    return e;
  }, [email, password]);

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    setError(null);
    const errs = validate();
    if (Object.keys(errs).length) { setFieldErr(errs); return; }
    setFieldErr({});
    setLoading(true);
    try {
      const res = await fetch('/api/v1/auth/login', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });
      const payload = await res.json();
      if (!res.ok) { setError(payload?.error?.message || 'Invalid email or password.'); return; }
      // Login success — navigate to dashboard
      window.location.href = '/dashboard';
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative font-sans" data-theme={darkMode ? 'dark' : 'light'}>
      <LoginBackground darkMode={darkMode} />

      <main className="relative z-10 min-h-screen flex items-center justify-center p-6
                        pt-[max(1.5rem,env(safe-area-inset-top))]
                        pb-[max(1.5rem,env(safe-area-inset-bottom))]"
            role="main">
        <div className="w-full max-w-[400px] bg-white dark:bg-[#1e1b2e] rounded-[18px]
                        shadow-card px-8 py-10 text-center"
             role="region" aria-labelledby="login-title">

          {/* Logo */}
          <div className="w-14 h-14 mx-auto mb-4 rounded-full flex items-center justify-center
                          text-2xl shadow-lg"
               style={{ background: 'linear-gradient(135deg,#43e8d8,#c471ed)' }}
               aria-hidden="true">
            🪐
          </div>

          <h1 id="login-title" className="text-[1.75rem] font-bold mb-8 tracking-tight
                                          text-gray-900 dark:text-gray-100">
            Login
          </h1>

          {/* Global error */}
          {error && (
            <div className="mb-5 px-4 py-3 rounded-lg text-sm text-left
                            bg-red-50 text-red-800 border border-red-200
                            dark:bg-red-950 dark:text-red-300 dark:border-red-800"
                 role="alert" aria-live="polite">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate aria-label="Login form">
            <Field
              id="email" label="Username" type="email"
              value={email} onChange={e => { setEmail(e.target.value); setFieldErr(f => ({ ...f, email: undefined })); }}
              placeholder="Type your email"
              autoComplete="email"
              error={fieldErr.email}
            />
            <Field
              id="password" label="Password" type="password"
              value={password} onChange={e => { setPassword(e.target.value); setFieldErr(f => ({ ...f, password: undefined })); }}
              placeholder="Type your password"
              autoComplete="current-password"
              error={fieldErr.password}
            />

            {/* Forgot */}
            <div className="text-right -mt-2 mb-6">
              <button type="button" onClick={() => navigate('forgot-password')}
                      className="text-sm text-gray-500 hover:text-violet-600 transition-colors
                                 focus-visible:outline-2 focus-visible:outline-violet-600 rounded">
                Forgot password?
              </button>
            </div>

            {/* Submit */}
            <button type="submit" disabled={loading}
                    className="btn-grad w-full h-12 rounded-full text-white font-bold
                               text-sm tracking-widest flex items-center justify-center gap-2
                               focus-visible:outline-3 focus-visible:outline-violet-600 focus-visible:outline-offset-2">
              {loading
                ? <span className="btn-spinner" aria-hidden="true" />
                : 'LOGIN'}
            </button>
          </form>

          {/* Social divider */}
          <div className="relative flex items-center text-gray-400 text-sm my-6">
            <span className="flex-1 border-t border-gray-200 dark:border-gray-600" />
            <span className="px-3">Or Sign Up Using</span>
            <span className="flex-1 border-t border-gray-200 dark:border-gray-600" />
          </div>

          {/* Social buttons — TODO: OAuth */}
          <div className="flex justify-center gap-4 mb-6" role="group"
               aria-label="Social sign in (coming soon)">
            {[
              { name: 'Facebook', bg: '#1877f2', icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                  <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
                </svg>
              )},
              { name: 'Twitter', bg: '#1da1f2', icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                  <path d="M23 3a10.9 10.9 0 0 1-3.14 1.53A4.48 4.48 0 0 0 16.34 3c-2.49 0-4.5 2.01-4.5 4.5 0 .35.04.7.11 1.02A12.78 12.78 0 0 1 3 4.89a4.48 4.48 0 0 0-.61 2.26c0 1.56.8 2.94 2 3.75a4.47 4.47 0 0 1-2.04-.56v.06c0 2.18 1.55 4 3.6 4.41a4.52 4.52 0 0 1-2.03.08 4.51 4.51 0 0 0 4.21 3.12A9.05 9.05 0 0 1 1 19.54a12.78 12.78 0 0 0 6.92 2.03c8.3 0 12.85-6.88 12.85-12.85 0-.2 0-.39-.01-.58A9.22 9.22 0 0 0 23 3z"/>
                </svg>
              )},
              { name: 'Google', bg: 'white', border: true, icon: (
                <svg width="18" height="18" viewBox="0 0 24 24">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                </svg>
              )},
            ].map(({ name, bg, border, icon }) => (
              <button key={name} type="button" disabled
                      aria-label={`Sign in with ${name} (coming soon)`}
                      className="w-11 h-11 rounded-full flex items-center justify-center
                                 shadow-md hover:-translate-y-0.5 transition-transform
                                 focus-visible:outline-3 focus-visible:outline-violet-600 focus-visible:outline-offset-2
                                 disabled:opacity-70"
                      style={{ background: bg, border: border ? '1px solid #e5e7eb' : undefined }}>
                {icon}
              </button>
            ))}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-5
                          text-sm text-gray-500 dark:text-gray-400">
            Or Sign Up Using
            <button type="button" onClick={() => navigate('register')}
                    className="block mx-auto mt-2 font-bold tracking-wide
                               text-gray-900 dark:text-gray-100
                               hover:text-violet-600 dark:hover:text-violet-400
                               focus-visible:outline-2 focus-visible:outline-violet-600 rounded">
              SIGN UP
            </button>
          </div>
        </div>
      </main>

      <DarkModeToggle darkMode={darkMode} onToggle={() => setDarkMode(d => !d)} />
    </div>
  );
}
