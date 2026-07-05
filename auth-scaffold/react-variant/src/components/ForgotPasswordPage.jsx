import { useState } from 'react';
import LoginBackground from './LoginBackground.jsx';
import DarkModeToggle  from './DarkModeToggle.jsx';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function ForgotPasswordPage({ navigate }) {
  const [email,   setEmail]   = useState('');
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const [success, setSuccess] = useState(null);
  const [fieldErr,setFieldErr]= useState({});
  const [darkMode,setDarkMode]= useState(
    () => window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    setError(null); setSuccess(null); setFieldErr({});
    if (!EMAIL_RE.test(email.trim())) {
      setFieldErr({ email: 'Please enter a valid email address.' });
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/v1/auth/forgot-password', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ email: email.trim().toLowerCase() }),
      });
      // Always show success to prevent email enumeration
      // TODO: Wire to real email provider
      await res.json();
      setSuccess('If an account exists for that email, a reset link has been sent.');
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative font-sans" data-theme={darkMode ? 'dark' : 'light'}>
      <LoginBackground darkMode={darkMode} />
      <main className="relative z-10 min-h-screen flex items-center justify-center p-6" role="main">
        <div className="w-full max-w-[380px] bg-white dark:bg-[#1e1b2e] rounded-[18px]
                        shadow-card px-8 py-10 text-center"
             role="region" aria-labelledby="fp-title">

          <div className="w-14 h-14 mx-auto mb-4 rounded-full flex items-center justify-center
                          text-2xl shadow-lg"
               style={{ background:'linear-gradient(135deg,#43e8d8,#c471ed)' }} aria-hidden="true">✉️</div>

          <h1 id="fp-title" className="text-[1.75rem] font-bold mb-2 tracking-tight text-gray-900 dark:text-gray-100">
            Reset Password
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
            Enter your email and we'll send you a reset link.
          </p>

          {error   && <div className="mb-4 px-4 py-3 rounded-lg text-sm text-left bg-red-50 text-red-800 border border-red-200" role="alert" aria-live="polite">{error}</div>}
          {success && <div className="mb-4 px-4 py-3 rounded-lg text-sm text-left bg-green-50 text-green-800 border border-green-200" role="status" aria-live="polite">{success}</div>}

          <form onSubmit={handleSubmit} noValidate aria-label="Password reset form" className="text-left">
            <div className="mb-6">
              <label htmlFor="fp-email" className="block text-sm font-medium text-gray-500 mb-0.5">Email</label>
              <div className={`relative flex items-center border-b-[1.5px] transition-colors
                ${fieldErr.email ? 'border-red-500' : 'border-gray-200 dark:border-gray-600 focus-within:border-violet-600'}`}>
                <span className="absolute left-0 text-gray-400 pointer-events-none flex items-center" aria-hidden="true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </span>
                <input id="fp-email" type="email"
                       className="field-underline w-full py-3 pr-2 text-base text-gray-900 dark:text-gray-100 dark:bg-transparent"
                       value={email} onChange={e => { setEmail(e.target.value); setFieldErr({}); }}
                       placeholder="you@example.com" autoComplete="email"
                       required aria-required="true" aria-invalid={!!fieldErr.email}
                       aria-describedby={fieldErr.email ? 'fp-email-error' : undefined} />
              </div>
              {fieldErr.email && <span id="fp-email-error" className="text-xs text-red-600 mt-1 block" role="alert">{fieldErr.email}</span>}
            </div>

            <button type="submit" disabled={loading}
                    className="btn-grad w-full h-12 rounded-full text-white font-bold text-sm tracking-widest
                               flex items-center justify-center gap-2
                               focus-visible:outline-3 focus-visible:outline-violet-600 focus-visible:outline-offset-2">
              {loading ? <span className="btn-spinner" aria-hidden="true" /> : 'SEND RESET LINK'}
            </button>
          </form>

          <div className="border-t border-gray-200 dark:border-gray-700 mt-6 pt-5
                          text-sm text-gray-500 dark:text-gray-400">
            Remember your password?
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
