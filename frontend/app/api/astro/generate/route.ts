import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export const runtime = 'nodejs';

function pythonExecutable(): string {
  if (process.env.PYTHON_EXECUTABLE) return process.env.PYTHON_EXECUTABLE;
  // Try repo-local venv (Windows then POSIX)
  const maybeWin = path.resolve(process.cwd(), '..', 'jyothishyam_env', 'Scripts', 'python.exe');
  const maybePosix = path.resolve(process.cwd(), '..', 'jyothishyam_env', 'bin', 'python');
  // Use whichever exists in the filesystem if available
  try {
    const fs = require('fs');
    if (fs.existsSync(maybeWin)) return maybeWin;
    if (fs.existsSync(maybePosix)) return maybePosix;
  } catch (e) {
    // ignore
  }
  return 'python';
}

export async function POST(req: Request): Promise<Response> {
  const body = await req.json().catch(() => ({}));

  // validate minimal inputs
  const lat = body.lat;
  const lon = body.lon;
  if (lat == null || lon == null) {
    return NextResponse.json({ error: 'lat and lon required' }, { status: 400 });
  }

  return new Promise((resolve) => {
    try {
      const py = pythonExecutable();
      // resolve runner path relative to repository root (frontend/..)
      const runner = path.resolve(process.cwd(), '..', 'systems', 'Parasara', 'tools', 'runner_api.py');
      // set PYTHONPATH so the child python can import the repo packages
      const env = { ...process.env, PYTHONPATH: path.resolve(process.cwd(), '..') };
      const child = spawn(py, [runner], { stdio: ['pipe', 'pipe', 'pipe'], env });

      const input = JSON.stringify(body);
      child.stdin.write(input);
      child.stdin.end();

      let stdout = '';
      let stderr = '';
      child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
      child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });

      child.on('close', (code) => {
        if (code !== 0) {
          console.error('runner stderr:', stderr);
          console.error('tried runner path:', runner);
          resolve(NextResponse.json({ error: 'runner failed', detail: stderr }, { status: 500 }));
          return;
        }
        try {
          const parsed = JSON.parse(stdout);
          resolve(NextResponse.json(parsed));
        } catch (e) {
          console.error('invalid json from runner', stdout, stderr);
          resolve(NextResponse.json({ error: 'invalid runner output' }, { status: 500 }));
        }
      });
    } catch (err: any) {
      resolve(NextResponse.json({ error: 'server error', detail: String(err) }, { status: 500 }));
    }
  });
}
