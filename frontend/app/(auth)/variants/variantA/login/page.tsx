"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginVariantA() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) return setError("Email and password are required.");
    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim().toLowerCase(), password }),
      });
      const payload = await res.json();
      if (!res.ok) return setError(payload?.error?.message || payload?.message || "Login failed.");
      router.push("/dashboard");
    } catch (e) {
      setError("Network error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gray-50">
      <div className="w-full max-w-sm bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-2">Welcome back</h2>
        <p className="text-sm text-gray-500 mb-4">Sign in to access your charts and readings.</p>
        {error && <div className="mb-3 text-sm text-red-700 bg-red-50 p-2 rounded">{error}</div>}
        <form onSubmit={submit}>
          <label className="block mb-3">
            <div className="text-sm text-gray-600">Email</div>
            <input className="mt-1 w-full border rounded px-3 py-2" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@example.com" />
          </label>
          <label className="block mb-3">
            <div className="text-sm text-gray-600">Password</div>
            <input type="password" className="mt-1 w-full border rounded px-3 py-2" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="••••••••" />
          </label>

          <button type="submit" disabled={loading} className="w-full mt-2 bg-indigo-600 text-white rounded-full py-2">
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-600"><a href="/forgot-password" className="text-indigo-600 underline">Forgot password?</a></p>
        <p className="mt-3 text-sm text-gray-600">Don't have an account? <a href="/register" className="text-indigo-600 underline">Create one</a></p>
      </div>
    </div>
  );
}
