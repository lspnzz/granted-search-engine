# Tech Debt

## Open

- Add a full local observability stack for logs, metrics, and traces after v1 harness checks are stable.
- Promote live search evals into a scheduled workflow once fixture evals are reliable.
- Replace broad CORS defaults with environment-specific origins in deployed agent endpoints.
- Persist pitch-agent state outside process memory before relying on multi-instance Cloud Run behavior.

## Cleanup Rules

- Prefer small shared helpers over duplicated external-service handling when a third copy appears.
- Prefer typed boundary validation over probing unknown JSON shapes in business logic.
- Keep generated or exploratory artifacts out of mandatory CI paths unless they are deterministic.
