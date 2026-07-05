"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

interface RegisterFormState {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  acceptTos: boolean;
}

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState<RegisterFormState>({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    acceptTos: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  function validate(): string | null {
    if (form.name.trim().length < 2) return "Name must be at least 2 characters.";
    const emailRe = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
    if (!emailRe.test(form.email)) return "Please enter a valid email address.";
    if (form.password.length < 8) return "Password must be at least 8 characters.";
    if (form.password !== form.confirmPassword) return "Passwords do not match.";
    if (!form.acceptTos) return "You must accept the Terms of Service.";
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    const v = validate();
    if (v) {
      setError(v);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name.trim(),
          email: form.email.trim().toLowerCase(),
          password: form.password,
        }),
      });

      const payload = await res.json();
      if (!res.ok) {
        const msg = payload?.error?.message || payload?.message || "Registration failed.";
        setError(msg);
        setLoading(false);
        return;
      }

      setSuccess("Account created — redirecting to login...");
      setTimeout(() => router.push("/login"), 1200);
    } catch (err) {
      console.error(err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 hero-bg relative">
      <div className="w-full auth-card card p-8">
        <h1 className="text-2xl font-semibold mb-2 text-text-primary">Create an account</h1>
        <p className="text-sm muted mb-4">Start your Jyothishyam journey — receive a small welcome credit.</p>

        {error && (
          <div className="mb-4 text-sm text-error bg-red-50 p-3 rounded">{error}</div>
        )}
        {success && (
          <div className="mb-4 text-sm text-success bg-green-50 p-3 rounded">{success}</div>
        )}

        <form onSubmit={handleSubmit}>
          <label className="block mb-2">
            <span className="text-sm muted">Full name</span>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="mt-1 block w-full rounded border px-3 py-2"
              placeholder="Arjun Nair"
              required
            />
          </label>

          <label className="block mb-2">
            <span className="text-sm muted">Email</span>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="mt-1 block w-full rounded border px-3 py-2"
              placeholder="you@example.com"
              required
            />
          </label>

          <label className="block mb-2">
            <span className="text-sm muted">Password</span>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="mt-1 block w-full rounded border px-3 py-2"
              placeholder="Strong password"
              required
            />
          </label>

          <label className="block mb-2">
            <span className="text-sm muted">Confirm password</span>
            <input
              type="password"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
              className="mt-1 block w-full rounded border px-3 py-2"
              placeholder="Confirm password"
              required
            />
          </label>

          <label className="flex items-center gap-2 mt-3 mb-4">
            <input
              type="checkbox"
              checked={form.acceptTos}
              onChange={(e) => setForm({ ...form, acceptTos: e.target.checked })}
              className="w-4 h-4"
            />
            <span className="text-sm muted">I agree to the <a className="underline" href="/terms">Terms of Service</a></span>
          </label>

          <button
            type="submit"
            disabled={loading}
            className="pill-btn"
          >
            {loading ? (
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
              </svg>
            ) : (
              "Create account"
            )}
          </button>
        </form>

        <p className="mt-4 text-sm text-text-muted">Already have an account? <a className="text-primary underline" href="/login">Log in</a></p>
      </div>
    </div>
  );
}
