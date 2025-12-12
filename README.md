# Granted: Search Engine

A serverless application that helps users find relevant EU grants based on their project pitches.

## How it works

The application exposes an HTTP endpoint via Google Cloud Run Functions. It takes a project pitch as input, generates vector embeddings using OpenAI, and performs a semantic search against a Pinecone vector database to return the most relevant grants.


## Environment setup (within each directory)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Deploy to Google Cloud Run Functions (from the root directory)

```bash
gcloud run deploy granted-search-engine \
    --source=./search-engine \
    --function=search_grants \
    --region=REGION \
    --base-image=python313 \
    --allow-unauthenticated \
    --set-env-vars="EU_GRANT_CHUNKS_INDEX_HOST=your_eu_grants_index_host_here,EU_GRANT_CHUNKS_NAMESPACE=your_eu_grants_namespace_here,OPENAI_API_KEY=your_openai_api_key_here" \
    --set-secrets="PINECONE_API_KEY=projects/PROJECT_ID/secrets/PINECONE_API_KEY/versions/latest,OPENAI_API_KEY=projects/PROJECT_ID/secrets/OPENAI_API_KEY/versions/latest"

```