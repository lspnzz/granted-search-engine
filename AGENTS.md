# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Repo Map

- [Architecture](ARCHITECTURE.md)
- [Docs index](docs/INDEX.md)
- [Reliability](docs/RELIABILITY.md)
- [Security](docs/SECURITY.md)
- [Evals](docs/EVALS.md)
- [Quality score](docs/QUALITY_SCORE.md)
- [Tech debt](docs/tech-debt.md)

## What This Is

Granted is a semantic search engine over EU grants. A user describes their project pitch, and the system finds matching EU funding opportunities using vector embeddings and Pinecone.

## Services

| Service | Directory | Runtime | Deployment |
|---|---|---|---|
| Data Pipeline | `data-pipeline/` | Python 3.12, `functions-framework` | Cloud Run (`gcloud run deploy`) |
| Search API | `search/` | Python 3.12, Firebase Functions | Firebase (`firebase deploy --only functions`) |
| Pitch Agent | `agent/` | Python 3.12, `functions-framework` | Cloud Run (`gcloud run deploy`) |
| Web Frontend | `web/` | Next.js 16, React 19 | Firebase App Hosting |

## Local Development

### Python Services

Each Python service has its own `requirements.txt` and should be run from the repo root:

```bash
# Create a venv (do this per service or share one)
python3.12 -m venv .venv
source .venv/bin/activate

# Install deps for the service you're working on
pip install -r ./search/requirements.txt
pip install -r ./data-pipeline/requirements.txt
pip install -r ./agent/requirements.txt

# Run a service locally
functions-framework --target=search_grants --source=search/main.py
functions-framework --target=run_pipeline --source=data-pipeline/main.py
functions-framework --target=refine_pitch --source=agent/main.py
```

Each service reads config from a `.env` file at its root (via `python-dotenv`).

### Web Frontend

```bash
cd web
npm install
npm run dev   # http://localhost:3000
npm run build
npm run lint
```

### Harness Checks

```bash
./scripts/check.sh
./scripts/smoke.sh
```

Use `GRANTED_HARNESS_MODE=mock` for deterministic local checks without live OpenAI, Pinecone, GCS, Google Auth, Cloud Run, or EU API dependencies.

## Configuration Pattern

All Python services follow: **Request body params override env vars**. Required env vars for each service:

**`search/` and `data-pipeline/`**: `OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, `PINECONE_NAMESPACE`, `MODEL_NAME`, `DIMENSIONS` (and `TOP_K`, `CHUNK_SIZE`, `CHUNK_OVERLAP` for their respective services).

**`agent/`**: `OPENAI_API_KEY`, `SEARCH_API_URL`, `AGENT_MODEL` (default: `gpt-4o-mini`), `AGENT_TEMPERATURE`. Optional LangSmith tracing: `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`.

**`web/`**: `SEARCH_API_URL`, `AGENT_API_URL`. The Next.js API routes proxy requests to these URLs using Google Auth ID tokens (for Cloud Run authentication).

## Architecture

### Data Flow

1. **Data Pipeline** (`data-pipeline/`): Fetches raw grants from the EU Funding & Tenders Portal API → cleans/chunks (LangChain text splitters) → embeds (OpenAI) → upserts to Pinecone. Can load from a local JSON file via `load_grants_from_file`.

2. **Search** (`search/`): Embeds the user's pitch (OpenAI) → queries Pinecone → returns ranked grants.

3. **Agent** (`agent/`): A LangGraph multi-turn conversational agent that gathers pitch info from the user, composes an optimized pitch, asks for approval, then calls the Search API. State phases: `gathering → composing → reviewing → searching → complete`. Each HTTP request invokes one graph turn; state is persisted in-memory via `MemorySaver` keyed by `thread_id`.

4. **Web** (`web/`): Next.js frontend with two API routes:
   - `/api/search` → proxies to `SEARCH_API_URL` (Firebase search function)
   - `/api/agent` → proxies to `AGENT_API_URL` (Cloud Run agent function)

### Key Files

- `search/src/embed.py` — OpenAI embedding logic
- `search/src/vectorstore.py` — Pinecone query logic
- `agent/src/graph.py` — LangGraph graph definition with all nodes and routing
- `agent/src/state.py` — `AgentState` TypedDict and `AgentRequest` Pydantic model
- `agent/src/tools.py` — `search_grants()` tool that calls the Search API
- `data-pipeline/src/extractors/eu_grants_fetcher.py` — EU API fetcher
- `data-pipeline/src/transformers/` — `clean.py`, `chunk.py`, `embed.py`, `augment.py`
- `data-pipeline/src/loaders/` — `objectstore.py` (GCS), `vectorstore.py` (Pinecone upsert)
- `web/lib/api.ts` — Frontend `searchGrants()` function
- `web/lib/agent-api.ts` — Frontend agent API functions

## Deployment

`search/` is deployed via Firebase (managed by `firebase.json`):
```bash
firebase deploy --only functions
```

`data-pipeline/` and `agent/` are deployed via Cloud Run (see `deploy.sh`):
```bash
gcloud run deploy data-pipeline --source=./data-pipeline --function=run_pipeline ...
gcloud run deploy pitch-agent --source=./agent --function=refine_pitch ...
```

Secrets (`OPENAI_API_KEY`, `PINECONE_API_KEY`, `LANGCHAIN_API_KEY`) are managed via Google Secret Manager and injected at deploy time.
