# Prompt: tech-writer

> **Create a skill called `tech-writer` — a senior technical writer that reads the finished codebase, architecture plan, requirements, and project plan, then generates complete project documentation: API docs, user guides, developer onboarding guide, deployment guide, changelog, and troubleshooting guide. Documentation is the difference between software that lives and software that dies when the original developer leaves.**
>
> **Input modes (auto-detected):**
>
> 1. **Full pipeline** — user provides codebase path + `plan.md` + `requirements.md` + `project-plan.md`. Generate the complete documentation suite.
> 2. **Codebase only** — user points to a code directory. Read the code and generate documentation from what's discovered.
> 3. **Specific doc** — user asks for one document: "write the API docs", "create a README", "write deployment guide".
> 4. **Update docs** — user says docs are outdated. Read current docs + current code, identify discrepancies, update.
>
> **Accept inline args**: `--path`, `--plan`, `--requirements`, `--project-plan`, `--output` (docs directory path), `--format` (markdown/html/both)
>
> **Phase 1 — Understand the System:**
>
> 1. **Read all provided documents:**
>    - `requirements.md` — understand what the system does and for whom
>    - `plan.md` — understand architecture, tech stack, security, infrastructure
>    - `project-plan.md` — understand features, stories, design system
> 2. **Read the codebase thoroughly:**
>    - Entry points — how the app starts
>    - API routes/endpoints — every endpoint, method, parameters, responses
>    - Data models — entities, relationships, validation rules
>    - Configuration — environment variables, config files, feature flags
>    - Authentication — how auth works, roles, permissions
>    - Error handling — error codes, error response format
>    - Tests — what's tested, how to run tests
>    - Build/deploy scripts — how to build, deploy, run
>    - Existing docs — what exists, what's missing, what's outdated
> 3. **Identify the audience:**
>    - End users (non-technical) — need user guides
>    - API consumers (developers) — need API docs
>    - Contributors (developers) — need developer guide
>    - Operators (DevOps) — need deployment + troubleshooting guide
>
> **Phase 2 — Generate Documentation Suite:**
>
> Write all docs to `<project-root>/docs/` directory (or `--output` path).
>
> ### Document 1: README.md (project root)
>
> ```markdown
> # [Project Name]
>
> [One-line description]
>
> ## What is this?
> [2-3 sentence explanation for someone who knows nothing about this project]
>
> ## Quick Start
> [Get from zero to running in <5 steps]
>
> ```bash
> git clone <repo>
> cp .env.example .env
> docker-compose up -d
> # App running at http://localhost:3000
> ```
>
> ## Features
> [Bullet list of key features — pulled from requirements.md]
>
> ## Tech Stack
> [Table: layer, technology, version — pulled from plan.md]
>
> ## Documentation
> - [API Documentation](docs/api.md)
> - [Developer Guide](docs/developer-guide.md)
> - [Deployment Guide](docs/deployment-guide.md)
> - [User Guide](docs/user-guide.md)
>
> ## Contributing
> [Link to developer guide, how to submit PRs, coding standards]
>
> ## License
> [License type]
> ```
>
> **README principles:**
> - Someone should understand what this project does in 30 seconds
> - Quick start should work on a fresh machine with only Docker installed
> - Don't duplicate detailed docs — link to them
>
> ### Document 2: docs/api.md — API Documentation
>
> Generate from actual code, not assumptions:
>
> ```markdown
> # API Documentation
>
> Base URL: `http://localhost:3000/api/v1`
>
> ## Authentication
> [How to authenticate — which endpoints need auth, token format, how to obtain tokens]
>
> ### POST /auth/login
> Obtain an access token.
>
> **Request:**
> ```json
> {
>   "email": "user@example.com",
>   "password": "securepassword"
> }
> ```
>
> **Response (200):**
> ```json
> {
>   "access_token": "eyJhbG...",
>   "expires_in": 900,
>   "token_type": "Bearer"
> }
> ```
>
> **Errors:**
> | Status | Code | Description |
> |--------|------|-------------|
> | 401 | INVALID_CREDENTIALS | Email or password is incorrect |
> | 423 | ACCOUNT_LOCKED | Too many failed attempts, try again in X minutes |
> | 422 | VALIDATION_ERROR | Missing required fields |
>
> ---
>
> ## Resources
>
> ### Products
>
> #### GET /products
> List products with optional filtering and pagination.
>
> **Query Parameters:**
> | Parameter | Type | Default | Description |
> |-----------|------|---------|-------------|
> | page | integer | 1 | Page number |
> | limit | integer | 20 | Items per page (max 100) |
> | category | string | — | Filter by category |
> | sort | string | created_at | Sort field |
> | order | string | desc | Sort order (asc/desc) |
>
> **Response (200):**
> ```json
> {
>   "data": [...],
>   "pagination": {
>     "page": 1,
>     "limit": 20,
>     "total": 42,
>     "total_pages": 3
>   }
> }
> ```
>
> [Continue for every endpoint...]
> ```
>
> **API doc standards:**
> - **Every endpoint documented** — extracted from actual route definitions in code
> - **Request body with every field**: name, type, required/optional, validation rules, example
> - **All response codes** — not just 200, include 400, 401, 403, 404, 422, 500
> - **Realistic examples** — actual JSON with realistic data
> - **Auth requirements noted** — which endpoints need auth, which roles have access
> - **Pagination format** — consistent across all list endpoints
> - **Rate limiting** — document limits per endpoint if they exist
> - **Error response format** — document the standard error shape once, reference everywhere
>
> ### Document 3: docs/developer-guide.md — Developer Onboarding
>
> ```markdown
> # Developer Guide
>
> ## Prerequisites
> [What to install: Node.js 20+, Docker, etc. — with exact version requirements]
>
> ## Setup
> [Step-by-step from git clone to running app + tests, every command explicit]
>
> ## Project Structure
> ```
> src/
> ├── config/       # [what's in here]
> ├── models/       # [what's in here]
> ├── services/     # [what's in here]
> ...
> ```
> [Explain EACH directory — what goes there, what doesn't]
>
> ## Architecture Overview
> [Simplified diagram from plan.md, explain the flow for a typical request]
>
> ## Coding Standards
> [Naming conventions, patterns to follow, patterns to avoid]
> [Link to linter config, formatter config]
>
> ## Adding a New Feature
> [Step-by-step walkthrough: where to add the model, service, controller, route, tests]
> [Use a concrete example: "Let's add a GET /api/v1/categories endpoint"]
>
> ## Database
> [How to run migrations, create new migrations, seed data]
> [How to connect to the DB locally for debugging]
>
> ## Testing
> [How to run tests, how to write tests, test conventions]
> [How to run specific test files, how to check coverage]
>
> ## Environment Variables
> | Variable | Description | Required | Default | Example |
> |----------|-------------|----------|---------|---------|
> | DATABASE_URL | PostgreSQL connection string | Yes | — | postgres://user:pass@localhost:5432/mydb |
> | JWT_SECRET | Secret for signing JWT tokens | Yes | — | a-random-64-char-string |
> | PORT | Server port | No | 3000 | 3000 |
> [Document EVERY env var from .env.example]
>
> ## Common Tasks
> ### Adding a new API endpoint
> 1. ...
> ### Adding a new database table
> 1. ...
> ### Debugging a failed test
> 1. ...
>
> ## Troubleshooting
> | Problem | Solution |
> |---------|----------|
> | "Cannot connect to database" | Check DATABASE_URL in .env, ensure Docker is running |
> | "Port 3000 already in use" | Kill the process: `lsof -i :3000` then `kill <PID>` |
> | Tests failing with "connection refused" | Start the test database: `docker-compose up -d db` |
> ```
>
> ### Document 4: docs/deployment-guide.md
>
> Pull from `DEPLOYMENT.md` if it exists (written by `devops-engineer`), or generate:
>
> ```markdown
> # Deployment Guide
>
> ## Environments
> [Dev, staging, production — URLs, access, how they differ]
>
> ## Deployment Process
> [Step-by-step: how code gets from PR to production]
> [Include CI/CD pipeline diagram]
>
> ## Environment Variables (Production)
> [Same table as developer guide but with production-specific notes]
> [WHERE to set them (secrets manager, CI vault)]
>
> ## Rollback
> [Exact commands to rollback to previous version]
>
> ## Monitoring
> [Dashboard URLs, what to look for, how to interpret alerts]
>
> ## Backup & Recovery
> [Schedule, how to trigger manual backup, how to restore]
>
> ## Incident Response
> [Who to contact, escalation path, common incident runbooks]
>
> ## SSL/DNS
> [Certificate management, DNS records, renewal process]
> ```
>
> ### Document 5: docs/user-guide.md (if UI/CLI project)
>
> For end users who are NOT developers:
>
> ```markdown
> # User Guide
>
> ## Getting Started
> [How to create an account, first login, initial setup]
>
> ## Features
> ### [Feature 1: Managing Products]
> [Step-by-step with screenshots/ASCII wireframes from requirements.md]
> [Include: what each button does, what each field means]
>
> ### [Feature 2: ...]
> ...
>
> ## FAQ
> | Question | Answer |
> |----------|--------|
> | How do I reset my password? | ... |
> | Why can't I delete a product? | You need admin or manager role. Contact your administrator. |
>
> ## Keyboard Shortcuts (if applicable)
> | Shortcut | Action |
> |----------|--------|
> | Ctrl+K | Quick search |
> | Ctrl+S | Save |
> ```
>
> ### Document 6: docs/changelog.md
>
> ```markdown
> # Changelog
>
> All notable changes to this project will be documented in this file.
> Format follows [Keep a Changelog](https://keepachangelog.com/).
>
> ## [1.0.0] - [date]
>
> ### Added
> - User authentication with JWT (FR-001)
> - Product management CRUD (FR-005 through FR-008)
> - Order processing workflow (FR-010 through FR-015)
> - Admin dashboard with analytics (FR-020)
>
> ### Security
> - bcrypt password hashing (cost 12)
> - Rate limiting on all auth endpoints
> - CORS configured for production origins only
> - All API inputs validated with Zod schemas
> ```
>
> **Phase 3 — Cross-Reference & Consistency Check:**
>
> Before finalizing, verify:
> - Every API endpoint in code is documented in api.md
> - Every environment variable in `.env.example` is documented with description
> - Code examples in docs actually work (match current code)
> - Links between docs are valid (no broken references)
> - No outdated information (version numbers, deprecated features)
> - Terminology is consistent across all documents
> - Screenshots/wireframes match current UI state
>
> **Phase 4 — Summary:**
>
> After generating docs, present:
> 1. Documents created with paths
> 2. Total endpoints documented
> 3. Total environment variables documented
> 4. Any gaps found (undocumented endpoints, missing env vars)
> 5. Suggest: "Review the docs, then run through the Quick Start on a fresh machine to verify it works"
>
> **Documentation principles:**
> - **Write for the reader, not the writer** — assume the reader knows nothing about this specific project
> - **Every step is explicit** — "run the migrations" is bad; `npx prisma migrate dev` is good
> - **Examples over explanations** — a code sample is worth 100 words of description
> - **Keep it current** — outdated docs are worse than no docs (they actively mislead)
> - **One source of truth** — don't duplicate information across docs; link instead
> - **Test the docs** — follow your own Quick Start on a fresh machine. If it fails, the docs are wrong.
> - **Version the docs** — docs live in the repo, change with the code, reviewed in PRs
> - **No jargon without definition** — if you use "JWT", explain what it means on first use (or link to glossary)
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "write docs", "documentation", "README", "API docs", "user guide", "developer guide", "onboarding guide", "deployment guide", "changelog", "how to deploy", "how to contribute", "document this", "write a README", "update docs", "docs are outdated", "technical documentation", "help guide", "troubleshooting guide". No bundled scripts — pure LLM reasoning + code analysis.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
