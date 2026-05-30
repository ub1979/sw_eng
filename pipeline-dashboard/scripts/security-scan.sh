#!/usr/bin/env bash
# Security Scan Orchestrator
# Runs pip-audit, bandit, and semgrep; generates reports in security-reports/

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS_DIR="$PROJECT_ROOT/security-reports"

mkdir -p "$REPORTS_DIR"

echo "=== Security Scan Started ==="
echo "Project root: $PROJECT_ROOT"
echo "Reports dir:  $REPORTS_DIR"
echo ""

# 1. pip-audit (dependency CVE scan)
echo "[1/3] Running pip-audit..."
if command -v pip-audit &>/dev/null; then
    pip-audit --desc -r "$PROJECT_ROOT/requirements.txt" \
        > "$REPORTS_DIR/pip-audit-latest.txt" 2>&1 || true
    echo "      pip-audit complete. See security-reports/pip-audit-latest.txt"
else
    echo "      WARNING: pip-audit not installed. Run: pip install pip-audit"
fi

# 2. bandit (Python SAST)
echo "[2/3] Running bandit..."
if command -v bandit &>/dev/null; then
    bandit -r "$PROJECT_ROOT/app/" -f txt \
        > "$REPORTS_DIR/bandit-latest.txt" 2>&1 || true
    echo "      bandit complete. See security-reports/bandit-latest.txt"
else
    echo "      WARNING: bandit not installed. Run: pip install bandit"
fi

# 3. semgrep (general security audit)
echo "[3/3] Running semgrep..."
if command -v semgrep &>/dev/null; then
    semgrep --config p/security-audit "$PROJECT_ROOT" \
        --json -o "$REPORTS_DIR/semgrep-latest.json" 2>/dev/null || true
    echo "      semgrep complete. See security-reports/semgrep-latest.json"
else
    echo "      WARNING: semgrep not installed. Run: pip install semgrep"
fi

# 4. Custom grep checks
echo "[4/4] Custom checks (shell=True, raw SQL)..."
if grep -rn 'shell=True' "$PROJECT_ROOT/app/" "$PROJECT_ROOT/tests/" 2>/dev/null; then
    echo "      FAIL: shell=True found in codebase."
    exit 1
else
    echo "      PASS: No shell=True found."
fi

SQL_PATTERN='execute\s*\(.*%s|execute\s*\(.*f\[.*\]'
if grep -rn -E "$SQL_PATTERN" "$PROJECT_ROOT/app/" 2>/dev/null; then
    echo "      FAIL: Possible raw SQL interpolation found."
    exit 1
else
    echo "      PASS: No raw SQL string interpolation detected."
fi

echo ""
echo "=== Security Scan Complete ==="
echo "Check the following reports:"
echo "  - $REPORTS_DIR/pip-audit-latest.txt"
echo "  - $REPORTS_DIR/bandit-latest.txt"
echo "  - $REPORTS_DIR/semgrep-latest.json"
