import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { NextResponse } from "next/server";

export const runtime = "nodejs";

const MAX_REQUEST_BYTES = 8_192;
const MAX_CHILD_OUTPUT_BYTES = 2 * 1024 * 1024;
const CHILD_TIMEOUT_MS = 45_000;
const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const TIME_PATTERN = /^(?:[01]\d|2[0-3]):[0-5]\d$/;

const SAFE_MESSAGES: Record<string, string> = {
  invalid_request: "The request could not be read.",
  invalid_date: "Enter a valid birth date in YYYY-MM-DD format.",
  invalid_time: "Enter a valid local birth time in HH:MM format.",
  invalid_coordinates:
    "Latitude must be -90 to 90 and longitude -180 to 180.",
  invalid_timezone:
    "Enter a valid IANA time zone, such as Asia/Kolkata.",
  consent_required: "Confirm consent before generating the reading.",
  invalid_place: "Keep the display place label to 120 characters or fewer.",
  request_too_large: "The request is too large.",
  generation_timeout: "The reading took too long to generate. Please try again.",
  generation_failed: "The reading could not be generated. Please try again.",
};

type SafeError = { error: { code: string; message: string } };

function safeError(code: string, status: number): NextResponse<SafeError> {
  const safeCode = SAFE_MESSAGES[code] ? code : "generation_failed";
  return NextResponse.json(
    { error: { code: safeCode, message: SAFE_MESSAGES[safeCode] } },
    { status },
  );
}

function validDate(value: unknown): value is string {
  if (typeof value !== "string" || !DATE_PATTERN.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return (
    parsed.getUTCFullYear() === year &&
    parsed.getUTCMonth() === month - 1 &&
    parsed.getUTCDate() === day
  );
}

function validTimezone(value: unknown): value is string {
  if (typeof value !== "string" || value.length === 0 || value.length > 64) {
    return false;
  }
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: value }).format();
    return true;
  } catch {
    return false;
  }
}

function validate(body: unknown): string | null {
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return "invalid_request";
  }
  const value = body as Record<string, unknown>;
  if (!validDate(value.dob)) return "invalid_date";
  if (typeof value.time !== "string" || !TIME_PATTERN.test(value.time)) {
    return "invalid_time";
  }
  const latitude = value.lat;
  const longitude = value.lon;
  if (
    typeof latitude !== "number" ||
    !Number.isFinite(latitude) ||
    latitude < -90 ||
    latitude > 90 ||
    typeof longitude !== "number" ||
    !Number.isFinite(longitude) ||
    longitude < -180 ||
    longitude > 180
  ) {
    return "invalid_coordinates";
  }
  if (!validTimezone(value.tz)) return "invalid_timezone";
  if (value.consent !== true) return "consent_required";
  if (
    typeof value.place !== "string" ||
    value.place.length > 120
  ) {
    return "invalid_place";
  }
  return null;
}

function pythonExecutable(repoRoot: string): string {
  if (process.env.PYTHON_EXECUTABLE) return process.env.PYTHON_EXECUTABLE;
  const candidates = [
    path.join(
      repoRoot,
      "jyothishyam_env",
      "prompt01-py311",
      "Scripts",
      "python.exe",
    ),
    path.join(repoRoot, "jyothishyam_env", "Scripts", "python.exe"),
    path.join(repoRoot, "jyothishyam_env", "bin", "python"),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? "python";
}

export async function POST(request: Request): Promise<Response> {
  const contentLength = Number(request.headers.get("content-length") ?? "0");
  if (Number.isFinite(contentLength) && contentLength > MAX_REQUEST_BYTES) {
    return safeError("request_too_large", 413);
  }

  let rawBody: string;
  try {
    rawBody = await request.text();
  } catch {
    return safeError("invalid_request", 400);
  }
  if (Buffer.byteLength(rawBody, "utf8") > MAX_REQUEST_BYTES) {
    return safeError("request_too_large", 413);
  }

  let body: unknown;
  try {
    body = JSON.parse(rawBody);
  } catch {
    return safeError("invalid_request", 400);
  }
  const validationCode = validate(body);
  if (validationCode) return safeError(validationCode, 400);

  const repoRoot = path.resolve(process.cwd(), "..");
  const runner = path.join(
    repoRoot,
    "systems",
    "Parasara",
    "tools",
    "runner_api.py",
  );

  return new Promise((resolve) => {
    let settled = false;
    let stdout = Buffer.alloc(0);
    let outputExceeded = false;

    const finish = (response: Response) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve(response);
    };

    let child;
    try {
      child = spawn(pythonExecutable(repoRoot), [runner], {
        stdio: ["pipe", "pipe", "pipe"],
        windowsHide: true,
        env: { ...process.env, PYTHONPATH: repoRoot },
      });
    } catch {
      resolve(safeError("generation_failed", 500));
      return;
    }

    const timer = setTimeout(() => {
      child.kill();
      finish(safeError("generation_timeout", 504));
    }, CHILD_TIMEOUT_MS);

    child.on("error", () => finish(safeError("generation_failed", 500)));
    child.stdin.on("error", () => finish(safeError("generation_failed", 500)));
    child.stdout.on("data", (chunk: Buffer) => {
      if (outputExceeded) return;
      if (stdout.length + chunk.length > MAX_CHILD_OUTPUT_BYTES) {
        outputExceeded = true;
        child.kill();
        return;
      }
      stdout = Buffer.concat([stdout, chunk]);
    });
    // Drain stderr, but never copy it into responses or application logs.
    child.stderr.on("data", () => undefined);

    child.on("close", (code) => {
      if (outputExceeded || code !== 0) {
        finish(safeError("generation_failed", 500));
        return;
      }
      try {
        const parsed = JSON.parse(stdout.toString("utf8"));
        if (parsed?.error?.code) {
          const status =
            parsed.error.code === "generation_failed" ? 500 : 400;
          finish(safeError(parsed.error.code, status));
          return;
        }
        finish(NextResponse.json(parsed));
      } catch {
        finish(safeError("generation_failed", 500));
      }
    });

    child.stdin.end(JSON.stringify(body));
  });
}
