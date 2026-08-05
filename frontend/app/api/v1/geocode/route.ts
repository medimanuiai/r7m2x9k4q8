import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json(
    {
      error: {
        code: "geocoding_unavailable",
        message:
          "Place lookup is not available in this MVP. Enter latitude, longitude, and an IANA time zone manually.",
      },
      results: [],
    },
    { status: 501 },
  );
}
