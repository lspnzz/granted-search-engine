# Reliability

## Local Harness

Use `GRANTED_HARNESS_MODE=mock` for fast, deterministic validation. Mock mode must not require OpenAI, Pinecone, GCS, Google Auth, Cloud Run, or the EU API.

## Request IDs

HTTP entrypoints should accept `X-Request-ID`, generate one when missing, include it in response headers, and pass it to downstream services.

## Logging

Services should emit JSON log events containing:

- `service`
- `event`
- `request_id`
- `duration_ms` when timing a request
- dependency status fields such as `mode`, `status`, or result counts

## Failure Handling

- Client input failures return 400 with validation details.
- External dependency failures are logged with request IDs and return a stable error shape.
- Tests should prefer dependency injection or mock mode over live network calls.
