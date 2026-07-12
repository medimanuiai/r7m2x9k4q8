"use client";

import React, { useState } from "react";

type Snapshot = any;

export default function AstroPage() {
  // Prefill with a common test record to speed up manual testing
  const [dob, setDob] = useState("1977-06-21");
  const [time, setTime] = useState("09:15");
  const [place, setPlace] = useState("Rajahmundry, Andhra Pradesh, India");
  const [lat, setLat] = useState<string|number>(16.9891);
  const [lon, setLon] = useState<string|number>(81.7894);
  const [tz, setTz] = useState("Asia/Kolkata");
  const [consent, setConsent] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [suryaChart, setSuryaChart] = useState<any | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!consent) {
      setError("Please confirm consent to process birth data.");
      return;
    }
    setLoading(true);
    try {
      const payload: any = { dob, time, consent };
      if (place) payload.place = place;
      if (lat !== "" && lon !== "") {
        payload.lat = Number(lat);
        payload.lon = Number(lon);
      }
      if (tz) payload.tz = tz;

      const res = await fetch('/api/astro/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const j = await res.json().catch(() => null);
        setError(j?.error || `Request failed: ${res.status}`);
        setLoading(false);
        return;
      }
      const data = await res.json();
      setSnapshot(data.snapshot || data);
      if (data.surya_chart) setSuryaChart(data.surya_chart);
    } catch (err) {
      setError("Network error during generation.");
    } finally {
      setLoading(false);
    }
  };

  // Simple place -> geocode helper (calls backend geocode if available)
  const handleResolvePlace = async () => {
    if (!place) return;
    try {
      const r = await fetch(`/api/v1/geocode?q=${encodeURIComponent(place)}`);
      if (!r.ok) return;
      const j = await r.json();
      if (j?.results?.length) {
        const best = j.results[0];
        setLat(best.lat);
        setLon(best.lon);
        if (best.tz) setTz(best.tz);
      }
    } catch (e) {
      // ignore
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 hero-bg relative">
      <div className="w-full auth-card card p-8">
        <h1 className="text-2xl font-semibold mb-2 text-text-primary text-center">Generate Astrology Snapshot</h1>
        <p className="text-sm muted mb-6 text-center">Enter birth details to generate an explainable Parasara snapshot.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm muted mb-1">Date of birth</label>
            <input type="date" value={dob} onChange={(e) => setDob(e.target.value)} className="w-full px-3 py-2 rounded border" />
          </div>

          <div>
            <label className="block text-sm muted mb-1">Time (local)</label>
            <input type="time" value={time} onChange={(e) => setTime(e.target.value)} className="w-full px-3 py-2 rounded border" />
          </div>

          <div>
            <label className="block text-sm muted mb-1">Place (city, country)</label>
            <div className="flex gap-2">
              <input value={place} onChange={(e) => setPlace(e.target.value)} className="flex-1 px-3 py-2 rounded border" />
              <button type="button" onClick={handleResolvePlace} className="pill-btn" style={{width: 'auto', padding: '0.5rem 0.8rem'}}>Resolve</button>
            </div>
            <div className="mt-2 text-sm muted">Or enter lat/lon manually below.</div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm muted mb-1">Latitude</label>
              <input value={lat as any} onChange={(e) => setLat(e.target.value)} className="w-full px-3 py-2 rounded border" />
            </div>
            <div>
              <label className="block text-sm muted mb-1">Longitude</label>
              <input value={lon as any} onChange={(e) => setLon(e.target.value)} className="w-full px-3 py-2 rounded border" />
            </div>
          </div>

          <div>
            <label className="block text-sm muted mb-1">Timezone (optional)</label>
            <input value={tz} onChange={(e) => setTz(e.target.value)} placeholder="Asia/Kolkata" className="w-full px-3 py-2 rounded border" />
          </div>

          <div className="flex items-center gap-3">
            <input id="consent" type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} />
            <label htmlFor="consent" className="text-sm muted">I consent to processing my birth data for astrology generation.</label>
          </div>

          {error && <div className="text-red-600 bg-red-50 p-2 rounded">{error}</div>}

          <div>
            <button disabled={loading} className="pill-btn">{loading ? 'Generating...' : 'Generate snapshot'}</button>
            <div className="mt-2 text-sm muted"><a href="/privacy" className="underline">Privacy & data</a></div>
          </div>
        </form>

        <div className="mt-6">
          <h2 className="text-lg font-medium">Result</h2>
          {snapshot ? (
            <div className="mt-3">
              <ResultViewer snapshot={snapshot} />
            </div>
          ) : (
            <div className="mt-2 text-sm muted">No snapshot yet.</div>
          )}
          {suryaChart && (
            <div className="mt-4">
              <h3 className="text-md font-medium">Surya (NDAstro) Chart</h3>
              <div className="mt-2 card p-3 text-sm">
                <div className="mb-2">Lagna: {suryaChart.lagna?.sign} {suryaChart.lagna?.degree}</div>
                <div className="overflow-auto max-h-48">
                  <table className="w-full text-xs">
                    <thead className="text-text-muted"><tr><th>Planet</th><th>Sign</th><th>Deg</th><th>House</th><th>Nakshatra</th></tr></thead>
                    <tbody>
                      {suryaChart.planets.map((p: any, i: number) => (
                        <tr key={i} className="border-t">
                          <td className="py-1">{p.name}</td>
                          <td>{p.sign}</td>
                          <td>{p.degree}</td>
                          <td>{p.house}</td>
                          <td>{p.nakshatra?.name} ({p.nakshatra?.pada})</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultViewer({ snapshot }: { snapshot: any }) {
  const [showFull, setShowFull] = useState(false);
  const summary = snapshot?.summary || snapshot?.domains?.career?.summary || '';
  const meta = snapshot?.meta || {};
  const download = () => {
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'parasara_snapshot.json';
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <div className="card p-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-slate-300">Summary</div>
          <div className="mt-1 text-base">{summary || '—'}</div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowFull(!showFull)} className="px-3 py-1 bg-slate-700 rounded">{showFull ? 'Hide' : 'Show'} JSON</button>
          <button onClick={download} className="px-3 py-1 bg-emerald-600 rounded">Download JSON</button>
        </div>
      </div>

      {showFull && (
        <pre className="mt-3 max-h-96 overflow-auto text-xs bg-slate-800 p-2 rounded">{JSON.stringify(snapshot, null, 2)}</pre>
      )}
      <div className="mt-2 text-xs muted">Engine: {meta.engine_version || 'n/a'} • Generated: {meta.generated_at || 'n/a'}</div>
    </div>
  );
}
