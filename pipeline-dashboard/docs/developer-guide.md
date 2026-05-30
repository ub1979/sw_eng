# Developer Guide

## Project Overview

The SDLC Pipeline Dashboard is a local-first web application that wraps a 9-agent LLM-driven software development lifecycle pipeline. Non-technical users describe software needs in plain English, select an AI model provider, and watch the entire build process unfold in real-time.

## Architecture

- **Backend**: FastAPI (Python 3.12+) with native SSE streaming
- **Database**: SQLite 3.53.1 with WAL mode
- **Frontend**: Vanilla ES modules + Alpine.js 3.15.12 (CDN)
- **Real-time**: Server-Sent Events (SSE) via FastAPI `EventSourceResponse`
- **Process Management**: asyncio subprocess for CLI providers, httpx for Ollama HTTP

## Project Structure

```
pipeline-dashboard/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Settings, env vars
│   ├── database.py          # SQLite schema + WAL mode
│   ├── models.py            # Pydantic v2 models
│   ├── dao.py               # Data access layer
│   ├── orchestrator.py      # Pipeline state machine
│   ├── guardrails.py        # Command allowlist + path sandbox
│   ├── providers.py         # LLM provider adapters
│   ├── agents/              # 9 pipeline agents
│   │   ├── base.py          # BaseAgent abstract class
│   │   ├── req_engineer.py
│   │   ├── sw_architect.py
│   │   ├── proj_manager.py
│   │   ├── sw_developer.py
│   │   ├── code_reviewer.py
│   │   ├── qa_engineer.py
│   │   ├── devops_engineer.py
│   │   └── tech_writer.py
│   └── routers/
│       ├── api.py           # REST endpoints
│       └── sse.py           # SSE stream endpoint
├── static/
│   ├── index.html           # Single-page app
│   ├── css/
│   │   └── design-system.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       └── sse.js
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── scripts/
├── data/                    # SQLite DB + backups
├── projects/                # Generated project folders
├── guardrails.json          # Command allowlist config
├── requirements.txt
├── requirements-dev.txt
├── Makefile
└── README.md
```

## Development Setup

```bash
# 1. Clone and enter project
cd pipeline-dashboard

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
make install          # production deps
make install-dev      # + test and security tools

# 4. Run tests
make test             # all tests
make test-unit        # unit tests only
make test-integration # integration tests only
make test-e2e         # Playwright E2E tests

# 5. Run security scan
make security-scan

# 6. Start dev server
make run              # uvicorn on localhost:8000
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PIPELINE_DB_PATH` | `data/pipeline.db` | SQLite database file |
| `PIPELINE_PROJECTS_DIR` | `projects` | Generated project folders root |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `CLAUDE_CLI_PATH` | `claude` | Claude Code CLI binary |
| `GEMINI_CLI_PATH` | `gemini` | Gemini CLI binary (auto-detects `agy`) |
| `PIPELINE_GUARD` | `guardrails.json` | Guardrails config file |
| `ENV` | `dev` | Environment: dev, staging, prod |
| `HOST` | `127.0.0.1` | Server bind address |
| `PORT` | `8000` | Server port |

Copy `.env.example` to `.env` and customize.

## Adding a New Agent

Agents inherit from `BaseAgent` in `app/agents/base.py`:

```python
from app.agents.base import BaseAgent

class MyAgent(BaseAgent):
    AGENT_NAME = "my_agent"
    SYSTEM_PROMPT = """You are a ..."""

    async def run(self, ctx):
        # 1. Read previous artifacts
        requirements = self.read_artifact(ctx, "requirements.md")

        # 2. Build prompt
        prompt = f"{self.SYSTEM_PROMPT}\n\n{requirements}"

        # 3. Stream to LLM
        content = ""
        async for chunk in ctx.provider.chat([...], stream=True):
            content += chunk.content
            ctx.log(chunk.content)

        # 4. Write output
        self.write_artifact(ctx, "my-output.md", content)

        # 5. Return result
        return AgentResult(
            status=AgentStatus.COMPLETED,
            artifact_paths=["my-output.md"],
        )
```

Then register in `app/config.py`:

```python
PIPELINE_AGENTS = [..., "my_agent"]
```

## Adding a New Provider

Implement the `LLMProvider` abstract base in `app/providers.py`:

```python
class MyProvider(LLMProvider):
    async def health_check(self) -> bool: ...
    async def list_models(self) -> list[str]: ...
    async def chat(self, messages, stream=True) -> AsyncIterator[StreamChunk]: ...
```

Register in the factory function `create_provider()`.

## Testing

### Unit Tests

Mock external dependencies. Use `pytest-asyncio` for async tests.

```python
@pytest.mark.asyncio
async def test_something():
    # Arrange
    provider = MockProvider()
    ctx = AgentContext(..., provider=provider)

    # Act
    result = await agent.run(ctx)

    # Assert
    assert result.status == AgentStatus.COMPLETED
```

### Integration Tests

Use `httpx.AsyncClient` against the FastAPI app:

```python
@pytest.mark.asyncio
async def test_api():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
```

### E2E Tests

Playwright drives the browser. Tests run against a live uvicorn server on a random port.

```python
def test_flow(page: Page, live_server):
    page.goto(live_server)
    page.click("text=Start Building")
    assert page.is_visible("text=Select AI Model")
```

## Guardrails Configuration

Edit `guardrails.json` to customize allowed commands:

```json
{
  "allowed_executables": ["python3", "node", "npm", "git", "docker"],
  "blocked_patterns": ["sudo", "rm -rf /", "curl.*\\|.*sh"],
  "blocked_arguments": ["--no-verify", "--insecure"],
  "max_command_length": 4096,
  "path_traversal_allowed": false
}
```

Reload without restart: `POST /api/guardrails/reload`.

## Contributing

1. Follow existing code style (snake_case, type hints, minimal comments)
2. Add tests for new code (>90% coverage)
3. Run `make security-scan` before committing
4. Update `docs/` if user-facing behavior changes

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: Directory 'static' does not exist` | Running pytest from wrong directory | `cd pipeline-dashboard && pytest` |
| `aiosqlite` teardown warnings | Event loop cleanup in test fixtures | Cosmetic — tests still pass |
| Playwright browsers missing | Chromium not installed | `playwright install chromium` |
| Provider not found | CLI binary not in `$PATH` | Install Ollama/Claude/Gemini CLI |
| SSE not connecting | CORS or proxy issue | Verify `HOST=127.0.0.1`, no reverse proxy blocking SSE |
