#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -x "$ROOT/.venv/bin/python" ]; then
  PYTHON_BIN="$ROOT/.venv/bin/python"
fi

cd "$ROOT"
GRANTED_HARNESS_MODE=mock "$PYTHON_BIN" evals/search_eval.py --mode smoke
GRANTED_HARNESS_MODE=mock "$PYTHON_BIN" -m pytest tests/test_mock_harness.py
