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


export async function searchGrants(pitch: string): Promise<SearchResponse> {
  const response = await fetch("/api/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ pitch }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Error searching grants: ${response.statusText}`);
  }

  return response.json();
}

