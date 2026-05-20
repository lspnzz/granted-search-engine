# Granted Architecture

Granted helps users find relevant EU funding opportunities from a project pitch.

## Services

| Service | Directory | Role | Runtime |
|---|---|---|---|
| Web | `web/` | Next.js UI and API proxy routes | Node.js |
| Search API | `search/` | Embeds a pitch and queries Pinecone | Firebase Functions, Python 3.12 |
| Embed API | `embed/` | Batch embedding endpoint used by search and pipeline | Firebase Functions, Python 3.12 |
| Pitch Agent | `agent/` | Multi-turn pitch refinement flow | Cloud Run, Python 3.12 |
| Data Pipeline | `data-pipeline/` | Fetch, clean, chunk, embed, and index grants | Cloud Run, Python 3.12 |

## Data Flow

1. `data-pipeline` fetches raw grants from the EU Funding & Tenders API or loads fixture/raw JSON from GCS.
2. It cleans grant fields, chunks descriptions, embeds chunks through `embed`, and upserts vectors to Pinecone.
3. `search` embeds a user pitch through `embed`, queries Pinecone, and returns ranked grant summaries.
4. `agent` gathers pitch details, composes a search pitch, asks for approval, then calls `search`.
5. `web` hosts the search UI and agent UI, proxying server-side requests to the Python services with Google ID tokens in live mode.

## Harness Mode

All services support `GRANTED_HARNESS_MODE=mock` for deterministic local checks. Mock mode avoids OpenAI, Pinecone, GCS, EU API, Google Auth, and Cloud Run dependencies by using repo fixtures under `tests/fixtures`.

Use live mode only when validating deployed infrastructure or fresh production data.

## Boundaries

- Validate request bodies at HTTP boundaries.
- Keep external-service clients behind small functions so tests can replace them.
- Return stable response shapes from public APIs.
- Emit structured JSON logs with request IDs for cross-service debugging.
- Keep notebooks exploratory; executable checks live in scripts or tests.
