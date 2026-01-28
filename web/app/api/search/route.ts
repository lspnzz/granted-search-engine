import { GoogleAuth } from 'google-auth-library';
import { NextRequest, NextResponse } from 'next/server';
import { getPostHogClient } from '@/lib/posthog-server';

export async function POST(req: NextRequest) {
  const posthog = getPostHogClient();

  // Get distinct ID from client-side PostHog header if available
  const distinctId = req.headers.get('X-POSTHOG-DISTINCT-ID') || 'anonymous';

  try {
    const body = await req.json();
    const { pitch } = body;

    const targetUrl = process.env.SEARCH_API_URL;
    if (!targetUrl) {
      console.error("SEARCH_API_URL is not defined");

      // Track server-side error
      posthog.capture({
        distinctId,
        event: 'server_search_error',
        properties: {
          error_type: 'configuration_error',
          error_message: 'SEARCH_API_URL is not defined',
        },
      });

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

      // Track server-side backend error
      posthog.capture({
        distinctId,
        event: 'server_search_error',
        properties: {
          error_type: 'backend_error',
          error_status: response.status,
          error_message: response.statusText,
          query: pitch,
        },
      });

      return NextResponse.json({ error: `Backend Error: ${response.statusText}` }, { status: response.status });
    }

    const data = await response.json();

    // Track successful server-side search
    posthog.capture({
      distinctId,
      event: 'server_search_completed',
      properties: {
        query: pitch,
        results_count: data.grants?.length || 0,
      },
    });

    return NextResponse.json(data);

  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Internal Server Error";
    console.error("Search API Error:", error);

    // Track server-side exception
    posthog.capture({
      distinctId,
      event: 'server_search_error',
      properties: {
        error_type: 'exception',
        error_message: errorMessage,
      },
    });

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}
