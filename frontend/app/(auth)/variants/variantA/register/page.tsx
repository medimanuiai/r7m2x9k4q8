"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterVariantA() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (name.trim().length < 2) return setError("Name must be at least 2 characters.");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return setError("Invalid email.");
    if (password.length < 8) return setError("Password must be at least 8 characters.");
    if (password !== confirm) return setError("Passwords do not match.");

    setLoading(true);
    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), email: email.trim().toLowerCase(), password }),
      });
      const payload = await res.json();
      if (!res.ok) return setError(payload?.error?.message || payload?.message || "Registration failed.");
      router.push("/login");
    } catch (e) {
      setError("Network error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gray-50">
      <div className="w-full max-w-sm bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-2">Create your account</h2>
        <p className="text-sm text-gray-500 mb-4">Quick signup — get started in seconds.</p>
        {error && <div className="mb-3 text-sm text-red-700 bg-red-50 p-2 rounded">{error}</div>}
        <form onSubmit={submit}>
          <label className="block mb-3">
            <div className="text-sm text-gray-600">Full name</div>
            <input className="mt-1 w-full border rounded px-3 py-2" value={name} onChange={(e)=>setName(e.target.value)} placeholder="Your full name" />
          </label>
          <label className="block mb-3">
            <div className="text-sm text-gray-600">Email</div>
            <input className="mt-1 w-full border rounded px-3 py-2" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@example.com" />
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="block mb-3">
              <div className="text-sm text-gray-600">Password</div>
              <input type="password" className="mt-1 w-full border rounded px-3 py-2" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="••••••••" />
            </label>
            <label className="block mb-3">
              <div className="text-sm text-gray-600">Confirm</div>
              <input type="password" className="mt-1 w-full border rounded px-3 py-2" value={confirm} onChange={(e)=>setConfirm(e.target.value)} placeholder="••••••••" />
            </label>
          </div>

          <button type="submit" disabled={loading} className="w-full mt-2 bg-indigo-600 text-white rounded-full py-2">
            {loading ? "Creating…" : "Create account"}
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-600">Already registered? <a href="/login" className="text-indigo-600 underline">Log in</a></p>
      </div>
    </div>
  );
}
