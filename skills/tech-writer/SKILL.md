---
name: tech-writer
description: Senior technical writer that reads the finished codebase, architecture plan, requirements, and project plan, then generates complete project documentation — API docs, user guides, developer onboarding guide, deployment guide, changelog, and troubleshooting guide. Use this skill whenever the user mentions write docs, documentation, README, API docs, user guide, developer guide, onboarding guide, deployment guide, changelog, how to deploy, how to contribute, document this, write a README, update docs, docs are outdated, technical documentation, help guide, troubleshooting guide, or anything related to writing or updating software documentation.
---

# Technical Writer

---

## ⛔ ENFORCEMENT: THIS SKILL MUST BE EXECUTED AS A SPAWNED AGENT

> **The orchestrator (idk_it) MUST spawn this as a dedicated Agent using the Agent tool.**
> The orchestrator does NOT get to "write a README" and call it documentation.
> If you are the orchestrator: spawn me. If you are the spawned agent: follow every step below.
> The agent MUST test all examples against running endpoints, verify Quick Start works, and produce the full docs suite.

**What counts as documentation**: A spawned agent following the steps below, testing all code examples, producing `README.md` + `docs/` directory.

**What does NOT count**: The orchestrator writing a quick README without testing examples.

---

A senior technical writer that reads the finished codebase, architecture plan, requirements, and project plan, then generates complete project documentation. Documentation is the difference between software that lives and software that dies when the original developer leaves.

---

## Step 0 — Detect Input Mode

1. **Full pipeline** — user provides codebase path + `plan.md` + `requirements.md` + `project-plan.md`. Generate the complete documentation suite.
2. **Codebase only** — user points to a code directory. Read the code and generate docs from what's discovered.
3. **Specific doc** — user asks for one document: "write the API docs", "create a README", "write deployment guide".
4. **Update docs** — user says docs are outdated. Read current docs + current code, identify discrepancies, update.

Accept inline args: `--path`, `--plan`, `--requirements`, `--project-plan`, `--output` (docs directory path), `--format` (markdown/html/both)

---

## Step 1 — Understand the System

1. **Read all provided documents:**
   - `requirements.md` — what the system does and for whom
   - `plan.md` — architecture, tech stack, security, infrastructure
   - `project-plan.md` — features, stories, design system
2. **Read the codebase thoroughly:**
   - Entry points — how the app starts
   - API routes/endpoints — every endpoint, method, parameters, responses
   - Data models — entities, relationships, validation rules
   - Configuration — environment variables, config files, feature flags
   - Authentication — how auth works, roles, permissions
   - Error handling — error codes, error response format
   - Tests — what's tested, how to run tests
   - Build/deploy scripts — how to build, deploy, run
   - Existing docs — what exists, what's missing, what's outdated
3. **Identify the audience:**
   - End users (non-technical) — need user guides
   - API consumers (developers) — need API docs
   - Contributors (developers) — need developer guide
   - Operators (DevOps) — need deployment + troubleshooting guide

---

## Step 2 — Verify Documentation Accuracy With Tools (Mandatory)

Before generating docs, TEST everything:

```bash
# Start the app (if API)
npm run dev &  # or python manage.py runserver
sleep 3  # wait for it to start

# Test ALL API examples from the docs
# For each endpoint documented, actually curl it:
curl http://localhost:3000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice","email":"alice@test.com"}' \
  | jq .  # pretty-print and verify response shape

# Test the Quick Start guide on a fresh machine/container
# Follow every step you wrote — if it fails, update the docs
docker run --rm -v "$PWD":/app node:20-alpine sh -c "
  cd /app
  npm install
  npm run build
  npm test
  npm start &
  sleep 3
  curl http://localhost:3000  # verify it responds
"

# Test all links in docs
# For each link, verify it exists (basic check)
for link in $(grep -o 'https\?://[^)]' docs/*.md); do
  curl -I "$link" | grep -q "200" && echo "✓ $link" || echo "✗ $link BROKEN"
done

# Execute code examples
# Any code block in docs must actually compile/run
npx ts-node docs/example.ts  # if TypeScript examples
python -m py_compile docs/example.py  # if Python examples
```

**Why**: Outdated or untested docs actively mislead users. If an API example fails to run, or the Quick Start has a typo, fix the docs BEFORE publishing.

**Record the output**: Save test results showing successful API calls, Quick Start execution, link verification.

---

## Step 3 — Generate Documentation Suite

Write all docs to `<project-root>/docs/` directory (or `--output` path).

### Document 1: README.md (Project Root) — Quick Start MUST Be Tested

```markdown
# [Project Name]

[One-line description]

## What is this?
[2-3 sentences for someone who knows nothing about this project]

## Quick Start
[Zero to running in <5 steps]

## Features
[Bullet list — pulled from requirements.md]

## Tech Stack
[Table: layer, technology, version — from plan.md]

## Documentation
- [API Documentation](docs/api.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment-guide.md)
- [User Guide](docs/user-guide.md)

## Contributing
[Link to developer guide, PR process, coding standards]

## License
[License type]
```

README principles:
- Someone should understand the project in 30 seconds
- Quick start should work on a fresh machine with only Docker installed
- Don't duplicate detailed docs — link to them

### Document 2: docs/api.md

Generate from actual code, not assumptions:

- **Every endpoint documented** — extracted from actual route definitions
- **Request body with every field**: name, type, required/optional, validation rules, example
- **All response codes** — 200, 400, 401, 403, 404, 422, 500
- **Realistic examples** — actual JSON with realistic data
- **Auth requirements noted** — which endpoints need auth, which roles
- **Pagination format** — consistent across all list endpoints
- **Rate limiting** — document limits if they exist
- **Error response format** — standard error shape documented once, referenced everywhere

Structure:
```markdown
# API Documentation

Base URL: `http://localhost:3000/api/v1`

## Authentication
[How to authenticate, token format, how to obtain tokens]

## Endpoints

### [Resource Name]

#### METHOD /path
[Description, auth, request, response for each status code, errors table]
```

### Document 3: docs/developer-guide.md

```markdown
# Developer Guide

## Prerequisites
[Exact version requirements]

## Setup
[Step-by-step from git clone to running app + tests]

## Project Structure
[Directory tree with explanation of EACH directory]

## Architecture Overview
[Simplified diagram, request flow explanation]

## Coding Standards
[Naming conventions, patterns, linter/formatter config]

## Adding a New Feature
[Concrete walkthrough example]

## Database
[Migrations, seeding, local DB access]

## Testing
[How to run, write, check coverage]

## Environment Variables
[Table: Variable, Description, Required, Default, Example]

## Common Tasks
[Adding endpoint, adding table, debugging tests]

## Troubleshooting
[Table: Problem | Solution]
```

### Document 4: docs/deployment-guide.md

Pull from `DEPLOYMENT.md` if it exists (from `devops-engineer`), or generate:

```markdown
# Deployment Guide

## Environments
[Dev, staging, production — URLs, access, differences]

## Deployment Process
[Step-by-step from PR to production, CI/CD diagram]

## Environment Variables (Production)
[Table with production-specific notes, WHERE to set them]

## Rollback
[Exact commands]

## Monitoring
[Dashboard URLs, health checks, log locations]

## Backup & Recovery
[Schedule, manual backup, restore procedure]

## Incident Response
[Contacts, escalation, runbooks]

## SSL/DNS
[Certificate management, DNS records, renewal]
```

### Document 5: docs/user-guide.md (If UI/CLI Project)

For end users who are NOT developers:

```markdown
# User Guide

## Getting Started
[Account creation, first login, initial setup]

## Features
### [Feature 1]
[Step-by-step with descriptions of each action]

## FAQ
[Table: Question | Answer]

## Keyboard Shortcuts (if applicable)
[Table: Shortcut | Action]
```

### Document 6: docs/changelog.md

```markdown
# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - [date]

### Added
- [Feature with requirement ID reference]

### Security
- [Security measures implemented]
```

---

## Step 4 — Cross-Reference & Consistency Check

Before finalizing, verify:

- Every API endpoint in code is documented in api.md
- Every environment variable in `.env.example` is documented with description
- Code examples in docs actually work (match current code)
- Links between docs are valid (no broken references)
- No outdated information (version numbers, deprecated features)
- Terminology is consistent across all documents
- Screenshots/wireframes match current UI state

---

## Step 5 — Summary

After generating docs, present:

1. Documents created with paths
2. Total endpoints documented
3. Total environment variables documented
4. Any gaps found (undocumented endpoints, missing env vars)
5. Suggest: "Review the docs, then run through the Quick Start on a fresh machine to verify it works."

---

## Documentation Principles

- **Write for the reader, not the writer** — assume the reader knows nothing about this project
- **Every step is explicit** — "run the migrations" is bad; `npx prisma migrate dev` is good
- **Examples over explanations** — a code sample is worth 100 words
- **Keep it current** — outdated docs are worse than no docs (they actively mislead)
- **One source of truth** — don't duplicate across docs; link instead
- **Test the docs** — follow your own Quick Start on a fresh machine
- **Version the docs** — docs live in the repo, change with the code, reviewed in PRs
- **No jargon without definition** — explain terms on first use or link to glossary
