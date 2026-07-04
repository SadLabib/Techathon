#!/usr/bin/env bash
# Run the backend and frontend together for local development.
# Usage: ./scripts/dev.sh   (Ctrl-C stops both)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "Starting backend on :$BACKEND_PORT ..."
(
  cd "$ROOT/backend"
  [ -d .venv ] || python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -q -r requirements.txt
  uvicorn main:app --reload --port "$BACKEND_PORT"
) &
BACKEND_PID=$!

echo "Starting frontend on :$FRONTEND_PORT ..."
(
  cd "$ROOT/frontend"
  [ -d node_modules ] || npm install
  VITE_API_BASE="http://localhost:$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT" --strictPort
) &
FRONTEND_PID=$!

# Stop both children on exit.
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' EXIT
wait
