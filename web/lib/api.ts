import { mockGrants } from "./mock-grants";

export interface Grant {
  id?: string;
  title?: string;
  description?: string;
  amount?: string;
  deadline?: string;
  match_score?: number;
  status?: string;
  url?: string;
  opening_date?: string;
}

export interface SearchResponse {
  pitch: string;
  grants: Grant[];
}


export class RateLimitError extends Error {
  isAuthenticated: boolean;
  constructor(message: string, isAuthenticated: boolean) {
    super(message);
    this.name = 'RateLimitError';
    this.isAuthenticated = isAuthenticated;
  }
}

export async function searchGrants(pitch: string, idToken?: string | null): Promise<SearchResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (idToken) {
    headers["Authorization"] = `Bearer ${idToken}`;
  }

  const response = await fetch("/api/search", {
    method: "POST",
    headers,
    body: JSON.stringify({ pitch }),
  });

  if (response.status === 429) {
    const errorData = await response.json().catch(() => ({}));
    throw new RateLimitError(
      errorData.error || 'Rate limit exceeded',
      errorData.isAuthenticated ?? false
    );
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Error searching grants: ${response.statusText}`);
  }

  return response.json();
}

