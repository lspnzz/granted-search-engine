#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export GRANTED_HARNESS_MODE="${GRANTED_HARNESS_MODE:-mock}"
export SEARCH_API_URL="${SEARCH_API_URL:-mock://search}"
export AGENT_API_URL="${AGENT_API_URL:-mock://agent}"

cd "$ROOT/web"
echo "Starting web dev server in GRANTED_HARNESS_MODE=$GRANTED_HARNESS_MODE"
echo "Open http://localhost:3000"
npm run dev
