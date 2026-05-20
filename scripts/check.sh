#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

cd "$ROOT"

"$PYTHON_BIN" scripts/check_docs.py
"$PYTHON_BIN" -m ruff check .
GRANTED_HARNESS_MODE=mock "$PYTHON_BIN" -m pytest
GRANTED_HARNESS_MODE=mock "$PYTHON_BIN" evals/search_eval.py --mode smoke

cd "$ROOT/web"
npm run lint
npm run typecheck
GRANTED_HARNESS_MODE=mock SEARCH_API_URL=mock://search AGENT_API_URL=mock://agent npm run build
GRANTED_HARNESS_MODE=mock SEARCH_API_URL=mock://search AGENT_API_URL=mock://agent npm run e2e
