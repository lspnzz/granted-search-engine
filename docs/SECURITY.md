# Security

## Secrets

Secrets are provided by Google Secret Manager in deployed environments and `.env` files locally. Do not commit real API keys, service account JSON, or Firebase private keys.

## Auth

The web API routes authenticate to Cloud Run and Firebase Functions with Google ID tokens in live mode. In `GRANTED_HARNESS_MODE=mock`, auth is bypassed only for deterministic local checks.

## Input Boundaries

HTTP handlers must validate payload size, required fields, and numeric bounds before calling external services.

## Data Handling

Search queries and pitches may contain commercially sensitive project ideas. Logs should include short previews or hashes rather than full pitch text unless explicitly needed for local debugging.
