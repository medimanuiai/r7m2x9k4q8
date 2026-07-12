"use client";

import React from "react";

export default function DashboardPage() {
  return (
    <div className="min-h-screen p-6 bg-slate-900 text-white">
      <div className="max-w-3xl mx-auto bg-slate-800/50 border border-slate-700 rounded p-6">
        <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
        <p className="text-sm text-slate-300 mb-4">Welcome — your account dashboard is a work in progress.</p>

        <div className="grid gap-3">
          <a className="px-4 py-2 bg-indigo-600 rounded w-max" href="/account/astro">Go to Astrology generator</a>
          <a className="text-sm text-slate-400" href="/account">Manage account</a>
        </div>
      </div>
    </div>
  );
}
