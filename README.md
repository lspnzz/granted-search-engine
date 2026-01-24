# Granted: Search Engine

A serverless application for semantic search over EU grants. It ingests grant data fetching from the European Commissions's Funding & Tenders Portal API, generates vector embeddings, and enables semantic search queries.

## Architecture

The system consists of two main Google Cloud Run Functions:

1.  **Data Pipeline** (`data-pipeline/`): An ETL pipeline that fetches raw grant data, cleans it, chunks it, embeds it using OpenAI embeddings, and indexes it into a Pinecone vector database.
2.  **Search Engine** (`search-engine/`): An API endpoint that accepts a project pitch, generates embeddings, and queries the Pinecone database for relevant grants.
3.  **Web Interface** (`web/`): A Next.js frontend application that allows users to interact with the search engine.

## Local Development

Prerequisites: Python 3.13+

### Setup

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r ./data-pipeline/requirements.txt
pip install -r ./search-engine/requirements.txt
```

### Web Client Setup

```bash
cd web
npm install
npm run dev
```

## Configuration

Both services are configured via JSON payloads.

### Data Pipeline Configuration (`/run_pipeline`)

Accepts a JSON body:
- `pinecone_index_name`: Name of the Pinecone index.
- `pinecone_namespace`: Namespace for the index.
- `chunk_size`: Size of text chunks.
- `chunk_overlap`: Overlap between chunks.
- `model_name`: OpenAI embedding model name.
- `dimensions`: Embedding dimensions.
- `load_grants_from_file`: (Optional) Path to a local file to load grants from instead of fetching.

### Search Engine Configuration (`/search_grants`)

Accepts a JSON body:
- `pitch`: The project pitch description to search for.
- `top_k`: Number of results to return.
- `model_name`: OpenAI embedding model name.
- `dimensions`: Embedding dimensions.
- `pinecone_index_name`: Target Pinecone index.
- `pinecone_namespace`: Target Pinecone namespace.

## License

This project is licensed under the MIT License with the Commons Clause 1.0. 
This means you are free to download, use, and modify the code for personal 
use, but you are strictly prohibited from selling the software or using 
it to provide a commercial service.

See the [LICENSE](LICENSE) file for the full text.