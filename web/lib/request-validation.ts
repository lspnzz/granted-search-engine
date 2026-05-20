import { AgentMessage } from './agent-api';

type ParseResult<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

export interface SearchPayload {
  pitch: string;
}

export interface AgentPayload {
  messages: AgentMessage[];
  thread_id: string;
}

export function parseSearchPayload(body: unknown): ParseResult<SearchPayload> {
  if (!body || typeof body !== 'object') {
    return { ok: false, error: 'Request body must be an object' };
  }
  const pitch = (body as { pitch?: unknown }).pitch;
  if (typeof pitch !== 'string' || !pitch.trim()) {
    return { ok: false, error: 'pitch must be a non-empty string' };
  }
  if (pitch.length > 8000) {
    return { ok: false, error: 'pitch must be at most 8000 characters' };
  }
  return { ok: true, value: { pitch: pitch.trim() } };
}

export function parseAgentPayload(body: unknown): ParseResult<AgentPayload> {
  if (!body || typeof body !== 'object') {
    return { ok: false, error: 'Request body must be an object' };
  }

  const payload = body as { messages?: unknown; thread_id?: unknown };
  if (typeof payload.thread_id !== 'string' || !payload.thread_id.trim()) {
    return { ok: false, error: 'thread_id must be a non-empty string' };
  }
  if (payload.thread_id.length > 120) {
    return { ok: false, error: 'thread_id must be at most 120 characters' };
  }
  if (!Array.isArray(payload.messages) || payload.messages.length === 0 || payload.messages.length > 40) {
    return { ok: false, error: 'messages must contain 1 to 40 items' };
  }

  const messages: AgentMessage[] = [];
  for (const message of payload.messages) {
    if (!message || typeof message !== 'object') {
      return { ok: false, error: 'each message must be an object' };
    }
    const role = (message as { role?: unknown }).role;
    const content = (message as { content?: unknown }).content;
    if (role !== 'user') {
      return { ok: false, error: 'message role must be user' };
    }
    if (typeof content !== 'string' || !content.trim() || content.length > 8000) {
      return { ok: false, error: 'message content must be 1 to 8000 characters' };
    }
    messages.push({ role, content: content.trim() });
  }

  return { ok: true, value: { messages, thread_id: payload.thread_id.trim() } };
}
