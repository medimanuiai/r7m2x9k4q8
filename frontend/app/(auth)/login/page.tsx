"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password, remember }),
      });

      const payload = await res.json();
      if (!res.ok) {
        setError(payload?.error?.message || "Invalid credentials.");
        setLoading(false);
        return;
      }

      // Backend should set tokens (httpOnly cookie) or return tokens here.
      // For now redirect to dashboard.
      router.push("/dashboard");
    } catch (err) {
      console.error(err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 hero-bg relative">
      <div className="w-full auth-card card p-8">
        <div className="flex items-center justify-center mb-6">
          <div className="w-16 h-16 flex items-center justify-center rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 3 L2 21 H22 L12 3 Z" fill="#ffffff" opacity="0.95"/></svg>
          </div>
        </div>
        <h1 className="text-2xl font-semibold text-text-primary mb-2 text-center">Sign in</h1>
        <p className="text-sm muted mb-6 text-center">Log in to access your charts and AI readings.</p>

        {error && <div className="mb-4 text-sm text-red-600 bg-red-50 p-2 rounded">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="input-with-icon">
            <label className="block text-sm muted mb-1">Email</label>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 6l9 6 9-6" stroke="#000" strokeOpacity=".5" strokeWidth="1.2" fill="none"/></svg>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              className="w-full px-3 py-2 rounded border"
              placeholder="you@example.com"
              required
            />
          </div>

          <div className="input-with-icon">
            <label className="block text-sm muted mb-1">Password</label>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="10" width="16" height="10" stroke="#000" strokeOpacity=".5" strokeWidth="1.2" fill="none"/><path d="M8 10V7a4 4 0 018 0v3" stroke="#000" strokeOpacity=".5" strokeWidth="1.2" fill="none"/></svg>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              className="w-full px-3 py-2 rounded border"
              placeholder="Your password"
              required
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm muted">
              <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="h-4 w-4 rounded" />
              Remember me
            </label>
            <a className="text-sm muted underline" href="/forgot-password">Forgot?</a>
          </div>

          <div>
            <button type="submit" disabled={loading} className="pill-btn">
              {loading ? "Signing in..." : "SIGN IN"}
            </button>
          </div>
        </form>

        <div className="mt-4 text-sm muted text-center">
          New here? <a className="underline" href="/register">Create an account</a>
        </div>
      </div>
    </div>
  );
}
