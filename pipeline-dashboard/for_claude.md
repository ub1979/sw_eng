# SDLC Pipeline Dashboard — Project Context

## What Was Built

A **web-based SDLC Pipeline Dashboard** that wraps a 9-agent AI-driven software development lifecycle pipeline. Non-technical users describe software needs in plain English, select an AI model provider, and watch the entire build process unfold in real time.

## Tech Stack

- **Backend**: FastAPI 0.136.3 with native SSE streaming
- **Database**: SQLite 3.53.1 with WAL mode, auto-backup
- **Frontend**: Vanilla ES modules + Alpine.js 3.15.12 (CDN, zero build step)
- **Testing**: pytest + pytest-asyncio + Playwright E2E (94 tests, all passing)
- **Security**: Bandit, pip-audit, semgrep scans clean

## Project Location

`/Users/u/funcoding/skills/pipeline-dashboard/`

## Key Architecture Decisions

1. **Provider Adapter Pattern**: `LLMProvider` abstract base with `OllamaProvider` (HTTP), `ClaudeProvider` (subprocess), `GeminiProvider` (subprocess)
2. **Guardrails Engine**: Allowlist-based command blocking + path sandboxing using `shlex.split()`
3. **Pipeline Orchestrator**: asyncio-based state machine with single-pipeline enforcement (no concurrent runs)
4. **Checkpoint System**: Pipeline pauses at req_engineer, sw_architect, qa_engineer for user approval
5. **Startup Auto-Cleanup**: Orphaned RUNNING and CHECKPOINT pipelines are marked as FAILED on app startup

## Bugs Fixed During Development

| Bug | File | Fix |
|-----|------|-----|
| Orphaned pipelines blocking new starts | `app/orchestrator.py` | `on_startup()` now handles both RUNNING and CHECKPOINT states |
| Gemini trust directory error | `app/providers.py` | Added `--skip-trust` flag to Gemini subprocess calls |
| Pipeline delete left orphaned folders | `app/dao.py` | Added `shutil.rmtree(project_dir)` to `PipelineDAO.delete()` |
| Invalid pytest version in dev deps | `requirements-dev.txt` | Fixed `pytest==9.0.3` to `pytest==8.4.2` |
| Claude/Gemini health checks failing in UI | `app/providers.py` | Changed from running actual prompts to `--version`/`--help` checks with 5s timeout |

## QA Skill Weaknesses Identified

The QA skill missed these issues because:
1. **Environment-specific testing**: Tested in a "warm" dev directory where Gemini CLI was already trusted
2. **State transition gaps**: Verified checkpoint persistence after restart but didn't test "start new pipeline while CHECKPOINT exists"
3. **API-vs-UX validation**: Confirmed API returned correct data but didn't verify error visibility in the UI

## How to Run

```bash
cd /Users/u/funcoding/skills/pipeline-dashboard
source .venv/bin/activate
make run        # uvicorn on localhost:8000
```

If port 8000 is in use:
```bash
PORT=8001 make run
```

Clear stuck pipelines:
```bash
rm -f data/pipeline.db data/pipeline.db-wal data/pipeline.db-shm
```

## Useful Commands

- `make test` — run all 94 tests
- `make test-unit` — unit tests only
- `make test-e2e` — Playwright E2E tests
- `make security-scan` — bandit + pip-audit + semgrep
- `make install-dev` — install test dependencies

## User's Environment

- Running via **Ollama** (primary provider)
- Also wants **Claude CLI** and **Gemini CLI** compatibility
- Wants non-technical users to be able to use this
- Plans to add login/password later (multi-user support)
- Uses `claude --plugin-dir /Users/u/funcoding/skills` to load the SDLC plugin
