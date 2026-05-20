# Granted Search Engine

Granted is a semantic search engine over EU grants. A user describes their project pitch, and the system finds matching EU funding opportunities using embeddings and Pinecone.

## Services

| Service | Directory | Runtime | Deployment |
|---|---|---|---|
| Web Frontend | `web/` | Next.js 16, React 19 | Firebase App Hosting |
| Search API | `search/` | Python 3.12, Firebase Functions | `firebase deploy --only functions:search` |
| Embed API | `embed/` | Python 3.12, Firebase Functions | `firebase deploy --only functions:embed` |
| Pitch Agent | `agent/` | Python 3.12, `functions-framework` | Cloud Run |
| Data Pipeline | `data-pipeline/` | Python 3.12, `functions-framework` | Cloud Run |

See [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/INDEX.md](docs/INDEX.md) for the repo-local system map.

## Local Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -r search/requirements.txt
pip install -r embed/requirements.txt
pip install -r data-pipeline/requirements.txt
pip install -r agent/requirements.txt

cd web
npm install
npm run dev
```

For deterministic frontend development without live OpenAI, Pinecone, GCS, or Cloud Run services:

```bash
./scripts/dev.sh
```

## Checks

```bash
./scripts/check.sh
./scripts/smoke.sh
```

`GRANTED_HARNESS_MODE=mock` makes checks use local fixtures in `tests/fixtures`.

## Configuration

Python services follow the same rule: request body params override environment variables.

Required live-mode environment variables:

- `search/`: `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, `PINECONE_NAMESPACE`, `EMBEDDINGS_SERVICE_URL`, `TOP_K`
- `embed/`: `OPENAI_API_KEY`, `MODEL_NAME`, `DIMENSIONS`
- `data-pipeline/`: `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, `PINECONE_NAMESPACE`, `EMBEDDINGS_SERVICE_URL`, `MODEL_NAME`, `DIMENSIONS`, `CHUNK_SIZE`, `CHUNK_OVERLAP`
- `agent/`: `OPENAI_API_KEY`, `SEARCH_API_URL`, `AGENT_MODEL`, `AGENT_TEMPERATURE`
- `web/`: `SEARCH_API_URL`, `AGENT_API_URL`

## Evals

Executable search evals live in `evals/search_eval.py`; notebooks under `evals/notebooks` are exploratory only.

```bash
GRANTED_HARNESS_MODE=mock python evals/search_eval.py --mode smoke
```

## License

This project is licensed under the MIT License with the Commons Clause 1.0.

See [LICENSE](LICENSE) for the full text.
