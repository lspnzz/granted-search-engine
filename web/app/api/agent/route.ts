import { GoogleAuth } from 'google-auth-library';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    const targetUrl = process.env.AGENT_API_URL;
    if (!targetUrl) {
      console.error("AGENT_API_URL is not defined");
      return NextResponse.json({ error: "Configuration Error" }, { status: 500 });
    }

    // Try to use Google Auth for Cloud Run, fall back to direct fetch for local dev
    let headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    try {
      const auth = new GoogleAuth();
      const client = await auth.getIdTokenClient(targetUrl);
      const idToken = await client.idTokenProvider.fetchIdToken(targetUrl);
      headers['Authorization'] = `Bearer ${idToken}`;
    } catch {
      // Running locally — no auth needed
      console.log("No Google Auth available, calling agent directly");
    }

    const response = await fetch(targetUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Agent backend error: ${response.status} ${errorText}`);
      return NextResponse.json(
        { error: `Agent Error: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Internal Server Error";
    console.error("Agent API Error:", error);
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
