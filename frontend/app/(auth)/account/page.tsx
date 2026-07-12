"use client";

import React, { useEffect, useState } from "react";

type UserProfile = {
  id: string;
  name: string;
  email: string;
  created_at: string;
};

export default function AccountPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch("/api/v1/auth/me");
        if (!res.ok) {
          setError("Failed to load profile.");
          setLoading(false);
          return;
        }
        const payload = await res.json();
        const user = payload.data;
        if (!mounted) return;
        setProfile(user);
        setName(user.name);
        setAvatarUrl(user.avatar_url || "");
      } catch (err) {
        setError("Network error.");
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/users/me", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, avatar_url: avatarUrl }),
      });
      if (!res.ok) {
        const p = await res.json();
        setError(p?.error?.message || "Failed to save profile.");
        setSaving(false);
        return;
      }
      const p = await res.json();
      setProfile(p.data);
    } catch (err) {
      setError("Network error.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="min-h-screen p-6 bg-slate-900 text-white">
      <div className="max-w-3xl mx-auto bg-slate-800/50 border border-slate-700 rounded p-6">
        <h1 className="text-xl font-semibold mb-4">Account</h1>
        <p className="text-sm text-slate-300 mb-6">Manage your profile and account settings.</p>

        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1">Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" />
          </div>

          <div>
            <label className="block text-sm text-slate-300 mb-1">Avatar URL</label>
            <input value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-700" />
          </div>

          <div>
            <button disabled={saving} onClick={handleSave} className="px-4 py-2 bg-indigo-600 rounded">{saving ? "Saving..." : "Save changes"}</button>
          </div>

          <div className="mt-6">
            <h2 className="text-lg font-medium">Account details</h2>
            <div className="mt-2 text-sm text-slate-300">Email: {profile?.email}</div>
            <div className="mt-1 text-sm text-slate-300">Member since: {new Date(profile?.created_at || "").toLocaleDateString()}</div>
          </div>

          <div className="mt-6">
            <h2 className="text-lg font-medium">Security</h2>
            <a className="text-indigo-400 underline" href="/change-password">Change password</a>
          </div>
        </div>
      </div>
    </div>
  );
}
