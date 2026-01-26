import { mockGrants } from "./mock-grants";

export interface Grant {
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
  // const apiUrl = process.env.NEXT_PUBLIC_SEARCH_API_URL;
  // if (!apiUrl) {
  //   throw new Error("NEXT_PUBLIC_SEARCH_API_URL is not defined");
  // }

  // // TODO(LS): Remove extra params after updating the backend.
  // const response = await fetch(apiUrl, {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  //   body: JSON.stringify({
  //     pitch,
  //     top_k: Number(process.env.NEXT_PUBLIC_SEARCH_TOP_K),
  //     model_name: process.env.NEXT_PUBLIC_SEARCH_MODEL_NAME,
  //     dimensions: Number(process.env.NEXT_PUBLIC_SEARCH_DIMENSIONS),
  //     pinecone_index_name: process.env.NEXT_PUBLIC_PINECONE_INDEX_NAME,
  //     pinecone_namespace: process.env.NEXT_PUBLIC_PINECONE_NAMESPACE,
  //   }),
  // });

  // if (!response.ok) {
  //   throw new Error(`Error searching grants: ${response.statusText}`);
  // }

  // return response.json();
  return Promise.resolve({ pitch, grants: mockGrants });
}
