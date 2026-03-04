export interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AgentResponse {
  messages: AgentMessage[];
  thread_id: string;
  phase: 'gathering' | 'composing' | 'reviewing' | 'searching' | 'complete';
  composed_pitch?: string;
  search_results?: Array<{
    id: string;
    title: string;
    match_score: number;
    amount?: string;
    deadline?: string;
    status?: string;
    url?: string;
    opening_date?: string;
  }>;
}

export async function sendAgentMessage(
  messages: AgentMessage[],
  threadId: string,
): Promise<AgentResponse> {
  const response = await fetch('/api/agent', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages,
      thread_id: threadId,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Agent error: ${response.statusText}`);
  }

  return response.json();
}
