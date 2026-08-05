"use client";

import React, { useMemo, useState } from "react";

type FormState = {
  dob: string;
  time: string;
  place: string;
  lat: string;
  lon: string;
  tz: string;
  consent: boolean;
};

type Planet = {
  name: string;
  sign: string;
  degree: number;
  house: number;
  nakshatra?: { name?: string; pada?: number };
};

type CareerIndicator = {
  rule_id?: string;
  contribution?: number;
  evidence?: Record<string, unknown>;
};

type ReadingResponse = {
  snapshot: {
    engine?: { engine_version?: string };
    meta?: { engine_version?: string };
    domains?: {
      career?: {
        summary?: string;
        score?: number;
        confidence?: number;
        indicators?: CareerIndicator[];
      };
    };
  };
  surya_chart: {
    metadata?: {
      ayanamsa?: string;
      ayanamsa_degrees?: number;
      birth_datetime_utc?: string;
      birth_location?: {
        latitude?: number;
        longitude?: number;
      };
    };
    lagna?: { sign?: string; degree?: number };
    planets?: Planet[];
  };
  birth?: {
    place?: string;
    display_location?: string;
    timezone?: string;
    local_datetime?: string;
    utc_datetime?: string;
  };
};

const EMPTY_FORM: FormState = {
  dob: "",
  time: "",
  place: "",
  lat: "",
  lon: "",
  tz: "",
  consent: false,
};

const SYNTHETIC_SAMPLE: FormState = {
  dob: "2001-02-03",
  time: "14:25",
  place: "Synthetic sample — not a real person",
  lat: "12.9716",
  lon: "77.5946",
  tz: "Asia/Kolkata",
  consent: false,
};

const CLIENT_ERRORS: Record<string, string> = {
  date: "Enter a valid birth date.",
  time: "Enter a valid local birth time.",
  lat: "Latitude must be a number from -90 through 90.",
  lon: "Longitude must be a number from -180 through 180.",
  tz: "Enter an IANA time zone, such as Asia/Kolkata.",
  place: "Keep the place label to 120 characters or fewer.",
  consent: "Confirm consent before generating the reading.",
};

function validateForm(form: FormState): string | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(form.dob)) return CLIENT_ERRORS.date;
  const parsedDate = new Date(`${form.dob}T00:00:00Z`);
  if (
    Number.isNaN(parsedDate.valueOf()) ||
    parsedDate.toISOString().slice(0, 10) !== form.dob
  ) {
    return CLIENT_ERRORS.date;
  }
  if (!/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(form.time)) {
    return CLIENT_ERRORS.time;
  }
  const latitude = Number(form.lat);
  if (form.lat.trim() === "" || !Number.isFinite(latitude) || latitude < -90 || latitude > 90) {
    return CLIENT_ERRORS.lat;
  }
  const longitude = Number(form.lon);
  if (form.lon.trim() === "" || !Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
    return CLIENT_ERRORS.lon;
  }
  if (!form.tz.trim() || form.tz.length > 64) return CLIENT_ERRORS.tz;
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: form.tz }).format();
  } catch {
    return CLIENT_ERRORS.tz;
  }
  if (form.place.length > 120) return CLIENT_ERRORS.place;
  if (!form.consent) return CLIENT_ERRORS.consent;
  return null;
}

function formatDegree(value: number | undefined): string {
  return typeof value === "number" ? `${value.toFixed(2)}°` : "—";
}

function friendlyRuleId(value: string | undefined): string {
  return (value || "Supporting indicator")
    .replaceAll("_", " ")
    .replace(/\bKethu\b/g, "Ketu")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function displayPlanetName(value: string): string {
  return value === "Kethu" ? "Ketu" : value;
}

function displayEvidenceValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map((item) => displayEvidenceValue(item)).join(", ") || "none";
  }
  if (value === "Kethu") return "Ketu";
  return String(value);
}

function describeEvidence(evidence: Record<string, unknown> | undefined): string {
  if (!evidence) return "Existing engine indicator.";
  const parts = Object.entries(evidence)
    .filter(([, value]) => value !== null && value !== undefined && value !== "")
    .map(([key, value]) => {
      const label = key.replaceAll("_", " ");
      const display = displayEvidenceValue(value);
      return `${label}: ${display}`;
    });
  return parts.join(" · ") || "Existing engine indicator.";
}

export default function BirthCareerPage() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reading, setReading] = useState<ReadingResponse | null>(null);

  const career = reading?.snapshot?.domains?.career;
  const indicators = useMemo(() => career?.indicators || [], [career]);
  const displayPlanets = useMemo(
    () =>
      (reading?.surya_chart?.planets || []).filter(
        (planet) => !["empty", "ascendant"].includes(planet.name.toLowerCase()),
      ),
    [reading],
  );
  const confirmedLocation = useMemo(() => {
    const apiDisplay = reading?.birth?.display_location?.trim();
    if (apiDisplay) return apiDisplay;
    const suppliedLabel = reading?.birth?.place?.trim();
    if (suppliedLabel) return suppliedLabel;
    const location = reading?.surya_chart?.metadata?.birth_location;
    if (
      typeof location?.latitude === "number" &&
      typeof location?.longitude === "number"
    ) {
      return `${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}`;
    }
    return "Coordinates unavailable";
  }, [reading]);

  const update = (field: keyof FormState, value: string | boolean) => {
    setForm((current) => ({ ...current, [field]: value }));
    setError(null);
  };

  const loadSample = () => {
    setForm(SYNTHETIC_SAMPLE);
    setReading(null);
    setError(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const clientError = validateForm(form);
    if (clientError) {
      setError(clientError);
      setReading(null);
      return;
    }

    setLoading(true);
    setError(null);
    setReading(null);
    try {
      const response = await fetch("/api/astro/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dob: form.dob,
          time: form.time,
          place: form.place.trim(),
          lat: Number(form.lat),
          lon: Number(form.lon),
          tz: form.tz.trim(),
          consent: form.consent,
        }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok) {
        setError(
          data?.error?.message ||
            "The reading could not be generated. Please try again.",
        );
        return;
      }
      setReading(data as ReadingResponse);
    } catch {
      setError("The service could not be reached. Check the local server and try again.");
    } finally {
      setLoading(false);
    }
  };

  const downloadJson = () => {
    if (!reading) return;
    const blob = new Blob([JSON.stringify(reading, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "synthetic-birth-career-reading.json";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="journey-shell">
      <section className="intro-panel">
        <p className="eyebrow">MVP-01 · Career only</p>
        <h1>From a birth moment to a focused Career reading.</h1>
        <p className="intro-copy">
          Confirm the exact location and time zone. We convert the local moment
          to UTC, build a Lahiri-sidereal chart, and pass it to the existing
          Parasara Career engine.
        </p>
        <div className="journey-steps" aria-label="Reading steps">
          <span><b>1</b> Birth details</span>
          <i aria-hidden="true">→</i>
          <span><b>2</b> Confirm location</span>
          <i aria-hidden="true">→</i>
          <span><b>3</b> Career result</span>
        </div>
        <aside className="privacy-note">
          <strong>No account. No saved profile.</strong>
          <span>Birth details are processed only for this request.</span>
        </aside>
      </section>

      <div className="content-grid">
        <section className="panel form-panel" aria-labelledby="birth-heading">
          <div className="section-heading">
            <div>
              <p className="step-label">Steps 1–2</p>
              <h2 id="birth-heading">Birth details &amp; location</h2>
            </div>
            <button className="secondary-button" type="button" onClick={loadSample}>
              Load synthetic sample
            </button>
          </div>
          <p className="helper">
            Start empty or use the clearly synthetic sample. The place label is
            display-only; coordinates and time zone control the calculation.
          </p>

          <form onSubmit={handleSubmit} noValidate>
            <div className="field-grid two-columns">
              <label>
                Birth date
                <input
                  type="date"
                  value={form.dob}
                  onChange={(event) => update("dob", event.target.value)}
                  disabled={loading}
                  required
                />
              </label>
              <label>
                Local birth time
                <input
                  type="time"
                  value={form.time}
                  onChange={(event) => update("time", event.target.value)}
                  disabled={loading}
                  required
                />
              </label>
            </div>

            <label>
              Place label <span className="optional">(display only)</span>
              <input
                type="text"
                value={form.place}
                onChange={(event) => update("place", event.target.value)}
                placeholder="City, region, country"
                maxLength={120}
                disabled={loading}
              />
            </label>

            <fieldset>
              <legend>Confirmed calculation location</legend>
              <div className="field-grid coordinate-grid">
                <label>
                  Latitude
                  <input
                    inputMode="decimal"
                    value={form.lat}
                    onChange={(event) => update("lat", event.target.value)}
                    placeholder="-90 to 90"
                    disabled={loading}
                    required
                  />
                </label>
                <label>
                  Longitude
                  <input
                    inputMode="decimal"
                    value={form.lon}
                    onChange={(event) => update("lon", event.target.value)}
                    placeholder="-180 to 180"
                    disabled={loading}
                    required
                  />
                </label>
                <label>
                  IANA time zone
                  <input
                    value={form.tz}
                    onChange={(event) => update("tz", event.target.value)}
                    placeholder="Asia/Kolkata"
                    maxLength={64}
                    disabled={loading}
                    required
                  />
                </label>
              </div>
              <p className="field-note">
                Place lookup is not available in this MVP. Enter all three
                calculation fields manually.
              </p>
            </fieldset>

            <label className="consent-row">
              <input
                type="checkbox"
                checked={form.consent}
                onChange={(event) => update("consent", event.target.checked)}
                disabled={loading}
              />
              <span>
                I consent to processing these birth details for this ephemeral
                astrology reading.
              </span>
            </label>

            {error && (
              <div className="error-banner" role="alert">
                <strong>Check the details</strong>
                <span>{error}</span>
              </div>
            )}

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" aria-hidden="true" />
                  Generating Career reading…
                </>
              ) : (
                "Generate Career reading"
              )}
            </button>
          </form>
        </section>

        <section className="panel result-panel" aria-labelledby="result-heading" aria-live="polite">
          <div className="section-heading">
            <div>
              <p className="step-label">Step 3</p>
              <h2 id="result-heading">Career result</h2>
            </div>
            {reading && <span className="success-chip">Generated</span>}
          </div>

          {!reading && !loading && (
            <div className="empty-state">
              <div className="chart-orbit" aria-hidden="true"><span>✦</span></div>
              <h3>Your focused reading will appear here</h3>
              <p>
                You’ll see Lagna, planet placements, and the existing Career
                engine result—without placeholder domains or empty sections.
              </p>
            </div>
          )}

          {loading && (
            <div className="loading-state">
              <span className="spinner dark" aria-hidden="true" />
              <h3>Calculating the sidereal chart</h3>
              <p>Converting local time to UTC and applying Lahiri ayanamsa.</p>
            </div>
          )}

          {reading && (
            <div className="reading">
              <div className="confirmed-location">
                <span>Confirmed birth context</span>
                <strong>{confirmedLocation}</strong>
                <small>
                  {reading.birth?.timezone} · {reading.birth?.local_datetime}
                </small>
              </div>

              <div className="lagna-card">
                <span className="lagna-symbol">L</span>
                <div>
                  <small>Lahiri-sidereal Lagna</small>
                  <strong>
                    {reading.surya_chart?.lagna?.sign || "—"}{" "}
                    {formatDegree(reading.surya_chart?.lagna?.degree)}
                  </strong>
                </div>
                <div className="ayanamsa">
                  <small>Ayanamsa applied</small>
                  <b>{formatDegree(reading.surya_chart?.metadata?.ayanamsa_degrees)}</b>
                </div>
              </div>

              <div className="result-section">
                <h3>Planet placements</h3>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Planet</th>
                        <th>Sign &amp; degree</th>
                        <th>House input</th>
                        <th>Nakshatra</th>
                      </tr>
                    </thead>
                    <tbody>
                      {displayPlanets.map((planet) => (
                        <tr key={planet.name}>
                          <td><strong>{displayPlanetName(planet.name)}</strong></td>
                          <td>{planet.sign} {formatDegree(planet.degree)}</td>
                          <td>{planet.house}</td>
                          <td>
                            {planet.nakshatra?.name || "—"}
                            {planet.nakshatra?.pada ? ` · Pada ${planet.nakshatra.pada}` : ""}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="career-card">
                <p className="eyebrow">Existing Parasara Career engine</p>
                <h3>{career?.summary || "Career result generated"}</h3>
                <div className="metric-grid">
                  <div>
                    <span>Engine score</span>
                    <strong>{career?.score ?? "—"}</strong>
                    <small>Engine value, not a probability</small>
                  </div>
                  <div>
                    <span>Engine confidence</span>
                    <strong>{career?.confidence ?? "—"}</strong>
                    <small>Engine value, not a probability</small>
                  </div>
                </div>
              </div>

              <div className="result-section evidence-section">
                <h3>Supporting indicators</h3>
                {indicators.length ? (
                  <ul>
                    {indicators.slice(0, 4).map((indicator, index) => (
                      <li key={`${indicator.rule_id}-${index}`}>
                        <strong>{friendlyRuleId(indicator.rule_id)}</strong>
                        <span>{describeEvidence(indicator.evidence)}</span>
                        {typeof indicator.contribution === "number" && (
                          <small>Engine contribution: {indicator.contribution}</small>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-evidence">
                    No supporting indicators available for this result.
                  </p>
                )}
              </div>

              <details className="advanced">
                <summary>Advanced</summary>
                <p>
                  Download the sanitized chart and Career result used in this
                  view. Internal paths and raw server errors are excluded.
                </p>
                <button className="secondary-button" type="button" onClick={downloadJson}>
                  Download JSON
                </button>
              </details>
            </div>
          )}
        </section>
      </div>
      <footer>
        MVP-01 supports Career only. Real place autocomplete and other astrology
        domains are intentionally outside this release.
      </footer>
    </div>
  );
}
