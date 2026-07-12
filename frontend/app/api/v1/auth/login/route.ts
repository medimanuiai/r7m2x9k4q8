import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const email = (body.email || '').toString().trim().toLowerCase();
    const password = (body.password || '').toString();

    // Load dev accounts file from auth-scaffold
    const accountsPath = path.join(process.cwd(), 'auth-scaffold', 'server', 'data', 'accounts.json');
    let accounts: any[] = [];
    try {
      const txt = fs.readFileSync(accountsPath, 'utf8');
      accounts = JSON.parse(txt || '[]');
    } catch (e) {
      // fallback: accept any credentials in dev
      const res = NextResponse.json({ success: true });
      res.headers.set('Set-Cookie', `auth_placeholder=${Buffer.from(email || 'dev').toString('base64')}; Path=/; HttpOnly; SameSite=Strict`);
      return res;
    }

    const match = accounts.find((a) => (a.email || '').toLowerCase() === email && (a.password || '') === password);
    if (!match) {
      return NextResponse.json({ error: { message: 'Invalid email or password.' } }, { status: 401 });
    }

    const res = NextResponse.json({ success: true });
    res.headers.set('Set-Cookie', `auth_placeholder=${Buffer.from(email).toString('base64')}; Path=/; HttpOnly; SameSite=Strict`);
    return res;
  } catch (err) {
    return NextResponse.json({ error: { message: 'Login failed' } }, { status: 500 });
  }
}
