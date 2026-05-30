# SDLC Pipeline Dashboard

A web-based control center that wraps a 9-agent LLM-driven software development lifecycle pipeline. Non-technical users describe software needs in plain English, select an AI model provider, and watch the entire build process unfold in real-time with visual progress tracking, per-agent logs, and checkpoint approvals.

## What This Is

The SDLC Pipeline Dashboard is a local-first, single-user web application that automates software development from idea to working code. It orchestrates eight specialized AI agents:

1. **Requirements Engineer** — Generates `requirements.md` from your description
2. **Software Architect** — Designs the tech stack and architecture plan
3. **Project Manager** — Breaks work into epics, stories, and tasks
4. **Software Developer** — Writes source code and tests
5. **Code Reviewer** — Reviews code and produces a review report
6. **QA Engineer** — Runs tests and generates a bug report
7. **DevOps Engineer** — Creates deployment configurations
8. **Tech Writer** — Writes final documentation and README

At checkpoints (after Requirements, Architecture, and QA), the pipeline pauses so you can review and approve the generated artifacts before continuing.

## Features

- **Landing page + interactive tutorial** for first-time users
- **Model provider selector** (Ollama, Claude CLI, Gemini CLI) with auto-detection and health checks
- **Real-time pipeline progress** via Server-Sent Events (SSE)
- **Checkpoint approvals** with artifact preview and change requests
- **Guardrails engine** with command allowlist and filesystem path sandboxing
- **SQLite persistence** with WAL mode for crash resilience and browser reconnect
- **Dark theme UI** with WCAG 2.1 AA color contrast and keyboard accessibility
- **Artifact browser** with inline preview, syntax highlighting, and ZIP download
- **Pipeline history** with delete confirmation and read-only replay

## Prerequisites

- **Python 3.12+**
- **Node.js** (for projects the pipeline generates that use npm/Node)
- One or more AI model providers:
  - **Ollama** — local LLM server (install from [ollama.com](https://ollama.com))
  - **Claude Code CLI** — Anthropic's CLI (install from [code.claude.com](https://code.claude.com))
  - **Gemini / Antigravity CLI** — Google's CLI or `agy` (install from [antigravity.dev](https://antigravity.dev))

## Installation

### Quick Start

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repo-url> pipeline-dashboard
   cd pipeline-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   make install
   # Or manually: pip install -r requirements.txt
   ```

4. Copy the example environment file and adjust as needed:
   ```bash
   cp .env.example .env
   ```

5. Start the server:
   ```bash
   make run
   # Or manually: uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

6. Open your browser to **http://localhost:8000**

### Development Install

For running tests and security scans:
```bash
make install-dev
# Or: pip install -r requirements.txt -r requirements-dev.txt
```

## Configuration

Configuration is managed via environment variables (`.env` file) and `guardrails.json`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///data/pipeline.db` | SQLite connection string |
| `PIPELINE_PROJECTS_DIR` | `projects` | Generated project folders root |
| `PIPELINE_DATA_DIR` | `data` | SQLite and backups root |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `CLAUDE_CLI_PATH` | `claude` | Claude CLI binary name/path |
| `GEMINI_CLI_PATH` | `gemini` | Gemini CLI binary name/path |
| `GUARDRAILS_FILE` | `guardrails.json` | Guardrails config path |
| `ENV` | `dev` | Environment mode: `dev`, `staging`, `prod` |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `8000` | Server port |

### Guardrails Configuration

`guardrails.json` controls which shell commands the pipeline agents are allowed to execute:

```json
{
  "allowed_executables": ["python3", "node", "npm", "git", "pytest", "docker"],
  "blocked_patterns": ["sudo", "rm -rf /", "curl.*\\|.*sh"],
  "blocked_arguments": ["--no-verify", "--insecure"],
  "max_command_length": 4096,
  "path_traversal_allowed": false
}
```

Reload without restarting the server via `POST /api/guardrails/reload`.

## Usage

### Starting a Pipeline

1. Open **http://localhost:8000** in your browser.
2. If this is your first visit, a 4-step tutorial will guide you.
3. Select your AI model provider (Ollama, Claude, or Gemini) and model.
4. Type a plain-English description of what you want to build.
5. Click **Start Pipeline**.

### Watching Progress

- The dashboard shows a progress bar and agent cards that update in real time.
- The active agent card pulses blue and shows a live log panel.
- Click any agent card to expand it and see details, sub-tasks, and artifacts.

### Checkpoint Approvals

When the pipeline reaches a checkpoint:
1. A modal appears with the generated artifact (e.g., `requirements.md`, `plan.md`).
2. Review the artifact in the scrollable preview pane.
3. Click **Approve & Continue** to proceed.
4. Or click **Request Changes**, type feedback, and submit to rewind and re-run that agent.

### Browser Resilience

- **Closing the browser tab does NOT abort the pipeline.** The backend continues execution.
- **Reopening the dashboard** loads the latest state from SQLite and resumes SSE streaming automatically.
- If the backend crashes and restarts, orphaned running pipelines are marked as failed so you can retry.

### Artifacts

When the pipeline completes:
- Click into the **Artifacts** tab to browse generated files.
- Markdown files render inline; code files get syntax highlighting; images display directly.
- Click **Download All as ZIP** to save the entire project folder.

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| "Ollama is not running" | Ollama server not started | Run `ollama serve` in a terminal |
| "Claude CLI not found" | Claude Code not installed | Install from [code.claude.com](https://code.claude.com) |
| "Guardrails blocked command" | Agent tried a non-allowlisted command | Review the command in the security event log; edit `guardrails.json` if it is safe |
| SSE not connecting / no live updates | Ad blocker or proxy issue | Disable ad blockers for `localhost:8000`; check browser console for CORS errors |
| Pipeline failed after retries | LLM provider disconnected or returned error | Click **Retry** on the failed agent card, or start a new pipeline with a different provider |
| SQLite database locked | WAL file growing | This is normal under load; WAL auto-checkpoints. Restart the server if it persists |

## Development

### Running Tests

```bash
# Unit tests (DAO, guardrails, providers, agents, orchestrator)
make test-unit

# Integration tests (API endpoints, SSE, full pipeline)
make test-integration

# E2E tests (Playwright browser automation)
make test-e2e

# All tests
make test-all
```

### Running Security Scans

```bash
make security-scan
```

This runs `pip-audit`, `bandit`, `semgrep`, and custom checks for `shell=True` and raw SQL interpolation. Reports are saved to `security-reports/`.

### Project Structure

```
pipeline-dashboard/
├── app/
│   ├── config.py          # Settings and constants
│   ├── database.py        # SQLite schema and connection (WAL mode)
│   ├── models.py          # Pydantic models
│   ├── dao.py             # Data access layer (parameterized queries)
│   ├── guardrails.py      # Guardrails engine (allowlist + sandbox)
│   ├── providers.py       # LLM provider adapters (Ollama, Claude, Gemini)
│   ├── orchestrator.py    # Pipeline state machine
│   ├── agents/            # 8 agent modules
│   ├── routers/
│   │   ├── api.py         # REST endpoints
│   │   └── sse.py         # SSE stream endpoint
│   └── main.py            # FastAPI app factory
├── static/                # Frontend (Alpine.js + Vanilla JS + CSS)
├── data/                  # SQLite DB
├── projects/              # Generated project folders
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/               # Startup and security scripts
├── docs/                  # Additional documentation
├── guardrails.json        # Default allowlist
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── Makefile               # Common tasks
```

## Architecture Overview

See [plan.md](/Users/u/funcoding/skills/plan.md) for the full architecture plan, including:

- Monolithic FastAPI backend with native SSE streaming
- SQLite with WAL mode for persistence and crash recovery
- Provider Adapter Layer for Ollama HTTP API and Claude/Gemini CLI subprocesses
- Guardrails Engine with `shlex.split()` allowlist and path sandboxing
- Pipeline Orchestrator state machine with immediate SQLite persistence
- Vanilla JS + Alpine.js frontend with zero build step

## Additional Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) — systemd, launchd, PM2, Docker
- [Security Overview](docs/SECURITY.md) — Architecture, guardrails, reporting issues
- [API Reference](docs/API.md) — OpenAPI docs and endpoint reference

## License

MIT
