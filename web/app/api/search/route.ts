import { GoogleAuth } from 'google-auth-library';
import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { getPostHogClient } from '@/lib/posthog-server';
import { verifyIdToken } from '@/lib/firebase-admin';
import { checkAndIncrementUsage } from '@/lib/rate-limit';
import { mockGrants } from '@/lib/mock-grants';
import { parseSearchPayload } from '@/lib/request-validation';

const STOP_WORDS = new Set(['a', 'and', 'are', 'for', 'in', 'of', 'or', 'the', 'to', 'we', 'with']);

function tokens(text: string): Set<string> {
  return new Set(
    text
      .toLowerCase()
      .match(/[a-z0-9]+/g)
      ?.filter((token) => token.length > 2 && !STOP_WORDS.has(token)) ?? []
  );
}

function rankMockGrants(pitch: string) {
  const pitchTokens = tokens(pitch);
  return mockGrants
    .map((grant) => {
      const grantTokens = tokens([
        grant.id,
        grant.title,
        grant.description,
        grant.status,
      ].filter(Boolean).join(' '));
      const score = [...pitchTokens].filter((token) => grantTokens.has(token)).length;
      return { grant: { ...grant, match_score: score }, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score || (a.grant.title ?? '').localeCompare(b.grant.title ?? ''))
    .slice(0, 5)
    .map(({ grant, score }, _index, ranked) => ({
      ...grant,
      match_score: ranked[0]?.score ? score / ranked[0].score : 0,
    }));
}

export async function POST(req: NextRequest) {
  const requestId = req.headers.get('X-Request-ID') || randomUUID();
  const responseHeaders = { 'X-Request-ID': requestId };

  // Get distinct ID from client-side PostHog header if available
  const distinctId = req.headers.get('X-POSTHOG-DISTINCT-ID') || 'anonymous';
  let posthog: ReturnType<typeof getPostHogClient> = null;

  try {
    const body = await req.json();
    const parsed = parseSearchPayload(body);
    if (!parsed.ok) {
      return NextResponse.json({ error: parsed.error }, { status: 400, headers: responseHeaders });
    }
    const { pitch } = parsed.value;

    if (process.env.GRANTED_HARNESS_MODE === 'mock') {
      return NextResponse.json(
        { pitch, grants: rankMockGrants(pitch) },
        { status: 200, headers: responseHeaders }
      );
    }

    posthog = getPostHogClient();

    // --- Rate limiting ---
    let userId: string | null = null;
    const authHeader = req.headers.get('authorization');
    if (authHeader?.startsWith('Bearer ')) {
      try {
        const decoded = await verifyIdToken(authHeader.slice(7));
        userId = decoded.uid;
      } catch {
        // Invalid token — treat as unauthenticated
      }
    }

    const clientIp = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim()
      || req.headers.get('x-real-ip')
      || 'unknown';

    const usage = await checkAndIncrementUsage(userId, clientIp);
    if (!usage.allowed) {
      return NextResponse.json(
        { error: 'Rate limit exceeded', isAuthenticated: usage.isAuthenticated },
        { status: 429, headers: responseHeaders }
      );
    }
    // --- End rate limiting ---

    const targetUrl = process.env.SEARCH_API_URL;
    if (!targetUrl) {
      console.error("SEARCH_API_URL is not defined");

      // Track server-side error
      posthog?.capture({
        distinctId,
        event: 'server_search_error',
        properties: {
          error_type: 'configuration_error',
          error_message: 'SEARCH_API_URL is not defined',
        },
      });

      return NextResponse.json({ error: "Configuration Error" }, { status: 500, headers: responseHeaders });
    }

    const auth = new GoogleAuth();
    const client = await auth.getIdTokenClient(targetUrl);
    const idToken = await client.idTokenProvider.fetchIdToken(targetUrl);

    const response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`,
        'X-Request-ID': requestId,
      },
      body: JSON.stringify({
        pitch
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} ${errorText} at ${targetUrl}`);

      // Track server-side backend error
      posthog?.capture({
        distinctId,
        event: 'server_search_error',
        properties: {
          error_type: 'backend_error',
          error_status: response.status,
          error_message: response.statusText,
          query: pitch,
        },
      });

      return NextResponse.json(
        { error: `Backend Error: ${response.statusText}` },
        { status: response.status, headers: responseHeaders }
      );
    }

    const data = await response.json();

    // Track successful server-side search
    posthog?.capture({
      distinctId,
      event: 'server_search_completed',
      properties: {
        query: pitch,
        results_count: data.grants?.length || 0,
      },
    });

    return NextResponse.json(data, { headers: responseHeaders });

  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Internal Server Error";
    console.error("Search API Error:", error);

    // Track server-side exception
    posthog?.capture({
      distinctId,
      event: 'server_search_error',
      properties: {
        error_type: 'exception',
        error_message: errorMessage,
      },
    });

    return NextResponse.json({ error: errorMessage }, { status: 500, headers: responseHeaders });
  }
}
