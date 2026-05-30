#!/usr/bin/env bash
# Simple startup script for SDLC Pipeline Dashboard
# Usage: ./scripts/start.sh [dev|prod]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV="${1:-dev}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

cd "$PROJECT_ROOT"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
MIN_VERSION="3.12"
if [ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$MIN_VERSION" ]; then
    echo "ERROR: Python 3.12+ is required. Found $PYTHON_VERSION"
    exit 1
fi

# Check virtual environment
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
fi

# Activate virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Install dependencies
if [ "$ENV" == "dev" ]; then
    echo "Installing development dependencies..."
    pip install -q -r requirements.txt -r requirements-dev.txt
else
    echo "Installing production dependencies..."
    pip install -q -r requirements.txt
fi

# Create required directories
mkdir -p "$PROJECT_ROOT/data"
mkdir -p "$PROJECT_ROOT/projects"
mkdir -p "$PROJECT_ROOT/logs"

# Check .env file
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        echo "WARNING: .env file not found. Copying from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    fi
fi

# Check guardrails.json
if [ ! -f "$PROJECT_ROOT/guardrails.json" ]; then
    echo "WARNING: guardrails.json not found. Creating default..."
    python3 -c "
import json
config = {
    'allowed_executables': [
        'python3', 'python', 'node', 'npm', 'npx', 'pip', 'pip3',
        'pytest', 'playwright', 'git', 'docker', 'docker-compose',
        'curl', 'wget', 'cat', 'ls', 'mkdir', 'cp', 'mv', 'rm',
        'touch', 'echo', 'find', 'grep', 'sed', 'awk', 'sort',
        'uniq', 'wc', 'tar', 'zip', 'unzip'
    ],
    'blocked_patterns': [
        'sudo', 'rm -rf /', 'curl.*\\\\|.*sh', 'curl.*\\\\|.*bash',
        'wget.*\\\\|.*sh', ':\\\\(\\\\):{ :|:\\& };:', 'mkfs',
        'dd if=/dev/zero', '> /dev/sda', '> /dev/null',
        'chmod 777 /', 'chown -R'
    ],
    'blocked_arguments': ['--no-verify', '--insecure', '-k'],
    'max_command_length': 4096,
    'path_traversal_allowed': False
}
with open('guardrails.json', 'w') as f:
    json.dump(config, f, indent=2)
"
fi

echo ""
echo "Starting SDLC Pipeline Dashboard ($ENV mode)..."
echo "Host: $HOST:$PORT"
echo ""

if [ "$ENV" == "dev" ]; then
    exec uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
else
    exec uvicorn app.main:app --host "$HOST" --port "$PORT" --workers 1
fi
