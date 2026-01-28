
import { GoogleAuth } from 'google-auth-library';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { pitch } = body;

    const targetUrl = process.env.SEARCH_API_URL;
    if (!targetUrl) {
      console.error("SEARCH_API_URL is not defined");
      return NextResponse.json({ error: "Configuration Error" }, { status: 500 });
    }

    const auth = new GoogleAuth();
    const client = await auth.getIdTokenClient(targetUrl);
    const idToken = await client.idTokenProvider.fetchIdToken(targetUrl);

    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify({
        pitch
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} ${errorText} at ${targetUrl}`);
      return NextResponse.json({ error: `Backend Error: ${response.statusText}` }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error("Search API Error:", error);
    return NextResponse.json({ error: error.message || "Internal Server Error" }, { status: 500 });
  }
}
