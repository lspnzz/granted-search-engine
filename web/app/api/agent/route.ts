import { GoogleAuth } from 'google-auth-library';
import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import { mockGrants } from '@/lib/mock-grants';
import { parseAgentPayload } from '@/lib/request-validation';

const mockThreads = new Map<string, 'gathering' | 'reviewing' | 'complete'>();

export async function POST(req: NextRequest) {
  const requestId = req.headers.get('X-Request-ID') || randomUUID();
  const responseHeaders = { 'X-Request-ID': requestId };

  try {
    const body = await req.json();
    const parsed = parseAgentPayload(body);
    if (!parsed.ok) {
      return NextResponse.json({ error: parsed.error }, { status: 400, headers: responseHeaders });
    }

    if (process.env.GRANTED_HARNESS_MODE === 'mock') {
      const lastUser = parsed.value.messages.at(-1);
      const currentPhase = mockThreads.get(parsed.value.thread_id) ?? 'gathering';
      const approved = /^(yes|search|go|ok|okay|approve|do it)/i.test(lastUser?.content ?? '');
      const hasPitchDetail = (lastUser?.content ?? '').length > 30 && !/^hello$/i.test(lastUser?.content ?? '');

      if (currentPhase === 'reviewing' && approved) {
        mockThreads.set(parsed.value.thread_id, 'complete');
        return NextResponse.json(
          {
            messages: [{ role: 'assistant', content: 'Found matching EU grants from the local harness.' }],
            thread_id: parsed.value.thread_id,
            phase: 'complete',
            search_results: mockGrants.slice(0, 3),
          },
          { status: 200, headers: responseHeaders }
        );
      }

      if (hasPitchDetail) {
        mockThreads.set(parsed.value.thread_id, 'reviewing');
        return NextResponse.json(
          {
            messages: [
              {
                role: 'assistant',
                content: 'Here is a mock search pitch for review. Say "yes" to search.',
              },
            ],
            thread_id: parsed.value.thread_id,
            phase: 'reviewing',
            composed_pitch: lastUser?.content,
            search_results: [],
          },
          { status: 200, headers: responseHeaders }
        );
      }

      mockThreads.set(parsed.value.thread_id, 'gathering');
      return NextResponse.json(
        {
          messages: [
            {
              role: 'assistant',
              content: 'What problem does your project solve, and what is novel about your approach?',
            },
          ],
          thread_id: parsed.value.thread_id,
          phase: 'gathering',
          search_results: [],
        },
        { status: 200, headers: responseHeaders }
      );
    }

    const targetUrl = process.env.AGENT_API_URL;
    if (!targetUrl) {
      console.error("AGENT_API_URL is not defined");
      return NextResponse.json({ error: "Configuration Error" }, { status: 500, headers: responseHeaders });
    }

    // Try to use Google Auth for Cloud Run, fall back to direct fetch for local dev
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Request-ID': requestId,
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
      body: JSON.stringify(parsed.value),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Agent backend error: ${response.status} ${errorText}`);
      return NextResponse.json(
        { error: `Agent Error: ${response.statusText}` },
        { status: response.status, headers: responseHeaders }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { headers: responseHeaders });

  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Internal Server Error";
    console.error("Agent API Error:", error);
    return NextResponse.json({ error: errorMessage }, { status: 500, headers: responseHeaders });
  }
}
