#!/usr/bin/env bash
#
# run.sh — start the SDLC Pipeline Dashboard.
#
# Usage:
#   ./run.sh              # start on http://127.0.0.1:8000 with auto-reload
#   PORT=8001 ./run.sh    # use a different port
#   HOST=0.0.0.0 ./run.sh # expose on the network
#   ./run.sh --prod       # production mode (no auto-reload)
#
set -euo pipefail

# Always run from the project directory (where this script lives).
cd "$(dirname "$0")"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"
VENV=".venv"
PROD=0
[ "${1:-}" = "--prod" ] && PROD=1

echo "==> SDLC Pipeline Dashboard"

# 1. Virtual environment — create it the first time, then reuse it.
if [ ! -f "$VENV/bin/activate" ]; then
  echo "==> Creating virtual environment ($VENV)..."
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# 2. Dependencies — install if FastAPI isn't importable yet.
if ! python -c "import fastapi" >/dev/null 2>&1; then
  echo "==> Installing dependencies..."
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
fi

# 3. Environment file — seed from the example on first run.
if [ ! -f .env ] && [ -f .env.example ]; then
  echo "==> Creating .env from .env.example (edit it to set models / fast-model tiers)"
  cp .env.example .env
fi

# 4. Warn (don't fail) if the port is already in use.
if command -v lsof >/dev/null 2>&1 && lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "!!  Port $PORT is already in use. Stop the other process or run: PORT=8001 ./run.sh"
  exit 1
fi

# 5. Start the server.
echo "==> Starting on http://$HOST:$PORT  (Ctrl+C to stop)"
if [ "$PROD" -eq 1 ]; then
  exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT" --workers 1
else
  exec python -m uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
fi
