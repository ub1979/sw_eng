# Changelog

## [0.1.0] — 2026-05-29

### Added

- **Web dashboard** — Single-page app with dark theme, real-time progress tracking, and checkpoint approvals
- **9-agent SDLC pipeline** — Requirements → Architect → Planner → Developer → Reviewer → QA → DevOps → Writer
- **Model provider selection** — Ollama (local), Claude CLI, Gemini/Antigravity CLI with auto-detection
- **Real-time SSE streaming** — Live progress bar, agent status cards, log panel with auto-scroll
- **Checkpoint system** — Pause at key phases for user approval; request changes to rewind and re-run agents
- **Guardrails engine** — Allowlist-based command blocking, path sandboxing, security event logging
- **Artifact management** — Browse, preview (Markdown, code, images), and download generated files as ZIP
- **Pipeline history** — View past runs, resume paused pipelines, delete with confirmation
- **Browser resilience** — Closing tab doesn't abort pipeline; reopening resumes from SQLite state
- **Tutorial overlay** — 4-step onboarding for non-technical users
- **Accessibility** — WCAG 2.1 AA compliance, keyboard navigation, ARIA labels, reduced-motion support
- **SQLite with WAL mode** — Zero-config local database with automatic backups
- **Testing** — 87 tests (unit, integration, E2E with Playwright)
- **Security** — Bandit, pip-audit, semgrep scans clean; no `shell=True`, no raw SQL
- **Deployment configs** — Dockerfile, docker-compose, systemd, launchd, PM2
- **Documentation** — README, API docs, developer guide, user guide, deployment guide, security guide

### Architecture

- FastAPI 0.136.3 backend with native SSE support
- SQLite 3.53.1 with WAL mode for concurrent reads
- Alpine.js 3.15.12 frontend with zero build step
- Pydantic v2 for strict validation
- httpx 0.28+ for async HTTP
- aiosqlite 0.22.1 for async SQLite

### Security

- Guardrails allowlist with `shlex.split()` command validation
- Path sandboxing prevents traversal outside project folders
- `shell=True` forbidden in all subprocess calls
- All SQL uses parameterized queries
- CSP headers, security middleware, CORS whitelist
- Input validation via Pydantic models

### Known Limitations

- Single-user, single-pipeline-at-a-time (MVP scope)
- No authentication system (local-only access)
- Docker build tested structurally but not executed live (no Docker daemon in dev env)
- `pytest-asyncio` + `aiosqlite` emit harmless teardown warnings in full-suite runs
- Pydantic class-based `Config` deprecation warning (upstream, cosmetic)

## Future Roadmap

- Multi-user authentication with JWT sessions
- Concurrent pipeline execution via Celery + Redis
- Interactive DAG builder for custom pipeline definitions
- Cost/usage tracking dashboard
- Mobile-native app
- Cloud deployment automation (AWS/GCP/Azure)
