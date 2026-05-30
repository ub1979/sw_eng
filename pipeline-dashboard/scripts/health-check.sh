#!/usr/bin/env bash
# Health check script for SDLC Pipeline Dashboard
# Usage: ./scripts/health-check.sh [HOST] [PORT]
# Exits 0 if healthy, 1 if unhealthy

set -euo pipefail

HOST="${1:-${HOST:-127.0.0.1}}"
PORT="${2:-${PORT:-8000}}"
BASE_URL="http://${HOST}:${PORT}"
HEALTH_URL="${BASE_URL}/api/health"

ERRORS=0

check_http() {
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}" 2>/dev/null || true)
    if [ "${code}" = "200" ]; then
        echo "[OK] HTTP health check passed (${HEALTH_URL})"
    else
        echo "[FAIL] HTTP health check failed (HTTP ${code:-no response} from ${HEALTH_URL})"
        ERRORS=$((ERRORS + 1))
    fi
}

check_process() {
    # Look for uvicorn running the app
    if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
        echo "[OK] Process is running"
    else
        echo "[FAIL] Process not found"
        ERRORS=$((ERRORS + 1))
    fi
}

check_disk_space() {
    local threshold=90
    local usage
    usage=$(df -P . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "${usage}" -lt "${threshold}" ]; then
        echo "[OK] Disk usage: ${usage}%"
    else
        echo "[WARN] Disk usage critical: ${usage}%"
        ERRORS=$((ERRORS + 1))
    fi
}

check_env() {
    if [ -f .env ]; then
        echo "[OK] .env file exists"
    else
        echo "[WARN] .env file missing (using defaults)"
    fi
}

echo "=== SDLC Pipeline Dashboard Health Check ==="
echo "Target: ${BASE_URL}"
echo ""

check_process
check_http
check_disk_space
check_env

echo ""
if [ "${ERRORS}" -eq 0 ]; then
    echo "=== HEALTHY ==="
    exit 0
else
    echo "=== UNHEALTHY (${ERRORS} issue(s)) ==="
    exit 1
fi
