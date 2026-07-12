import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') || '';

  // Simple canned responses for common test queries
  const normalized = q.trim().toLowerCase();
  if (normalized.includes('rajahmundry')) {
    return NextResponse.json({
      results: [
        { display_name: 'Rajahmundry, East Godavari, Andhra Pradesh, India', lat: 16.9891, lon: 81.7894, tz: 'Asia/Kolkata' }
      ]
    });
  }

  // Fallback generic location (Bangalore)
  return NextResponse.json({
    results: [
      { display_name: q || 'Bengaluru', lat: 12.9716, lon: 77.5946, tz: 'Asia/Kolkata' }
    ]
  });
}
