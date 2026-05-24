# SDLC Skills System — Ready for Use

**Status**: ✅ Complete and operational

Generated: 2026-04-05

---

## What You Have

A complete software development lifecycle automation system with **9 skills**:

### Core Pipeline (8 SDLC Skills)

1. **`req-engineer`** — Intelligent requirements gathering
   - Conducts multi-round interviews
   - Extracts functional & non-functional requirements
   - Generates prototypes (ASCII wireframes, API specs, CLI examples)
   - Output: `requirements.md`

2. **`sw-architect`** — Architecture design
   - Analyzes requirements & existing codebase
   - Designs scalable, secure architecture
   - Creates ADRs (Architecture Decision Records)
   - Runs SAST tools (Semgrep, Bandit) to verify decisions
   - Output: `plan.md`

3. **`proj-manager`** — Project planning
   - Breaks down work into epics, stories, tasks
   - Creates design system specs for UI projects
   - Validates design choices with component libraries
   - Produces sprint plan with estimates
   - Output: `project-plan.md`

4. **`sw-developer`** — Implementation
   - Implements code one task at a time
   - Writes unit tests (>90% coverage)
   - Follows project conventions & architectural patterns
   - Verifies code compiles and tests pass
   - Output: Working code + test results

5. **`code-reviewer`** — Quality assurance
   - Reviews all code against architecture plan
   - Runs tests, linters, SAST tools
   - Checks security, performance, architectural compliance
   - Produces detailed review-report.md with fix guidance
   - Output: `review-report.md`

6. **`qa-engineer`** — Testing (Project-Type Aware)
   - **Auto-detects project type**: web app, API, CLI, desktop, mobile, library
   - **Web apps**: Playwright for UI automation + curl for APIs + direct DB queries
   - **APIs**: httpx/curl for all endpoints + database verification
   - **CLI tools**: Direct command execution + output validation
   - **Mobile/Desktop**: Framework-specific testing tools
   - All bugs reported with tool output as evidence
   - Output: `bug-report.md`

7. **`devops-engineer`** — Production readiness
   - Builds & verifies Docker images
   - Sets up CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
   - Tests pipelines with `act`
   - Configures monitoring, alerting, backup/recovery
   - Tests health checks and rollback procedures
   - Output: `DEPLOYMENT.md` + working CI/CD + Docker setup

8. **`tech-writer`** — Documentation
   - Tests API examples against running endpoints
   - Runs Quick Start guide on fresh machine
   - Verifies all code examples compile/execute
   - Checks all links work
   - Produces README, API docs, developer guide, deployment guide
   - Output: Complete docs suite

### Orchestration (1 Master Skill)

9. **`idk_it`** — SDLC Pipeline Orchestrator
   - **Entry point for all software work**
   - Detects intent: `new` (build from scratch), `add` (feature), `modify` (refactor), `fix` (bugs), `deploy`, `review`, `test`, `docs`
   - Auto-detects project state (existing requirements? design? code?)
   - **Manages tools** — auto-installs Node.js, Python, Go, Docker, Git, PostgreSQL/MySQL, Playwright, pytest, SAST tools
   - **Handles failures** — detects errors, attempts auto-fix, retries, escalates if unrecoverable
   - **Enforces evidence** — every claim backed by tool output, no "I read the code and it looks right"
   - Spawns agents sequentially or in parallel as needed
   - Checkpoints at decision points (requirements approval, architecture review, QA verdict)

---

## Key Features

### ✅ Tool-First Philosophy
Every agent MUST execute with real tools:
- Tests run and pass before "implementation complete"
- Code reviewed by linters, SAST, and human review
- Security scanned by Bandit, Semgrep, npm audit
- Docker images built and verified to start
- API examples tested against live endpoints
- Database changes verified with actual queries
- UI tested with Playwright automation

### ✅ Project-Type Detection
QA agent automatically detects and adapts to:
- Web applications (Playwright + curl + DB queries)
- REST APIs (httpx/curl + response validation + DB verification)
- CLI tools (direct execution + output parsing)
- Mobile apps (framework-specific tools)
- Desktop applications (OS-specific tools)
- Libraries (unit test suites + integration tests)
- Multi-service systems (per-service testing)

### ✅ Error Recovery
When tools fail:
1. Analyzes error (missing dependency? syntax error? network issue?)
2. Attempts auto-fix (install missing pkg, clear cache, etc.)
3. Retries command
4. If fixed → agent continues seamlessly
5. If still failing → escalates with clear error + suggested fix

### ✅ Design System Validation
For UI projects:
- Tests color contrast (WCAG AA compliance)
- Validates responsive breakpoints with real HTML
- Tests component library choices
- Verifies font sizes, spacing, shadows match spec

---

## How to Use

### Option 1: Start a New Project

When ready to build, invoke the skills in this order:

```
User: "I want to build [idea]"
↓
/req-engineer → Multi-round interview → requirements.md
↓
Checkpoint: Review requirements.md
↓
/sw-architect → Design architecture → plan.md
↓
Checkpoint: Review & approve plan
↓
/proj-manager → Break down work → project-plan.md
↓
Checkpoint: Review task estimates & timeline
↓
/sw-developer → Implement tasks → working code
↓
/code-reviewer → Review all code → review-report.md
↓
(If issues found, /sw-developer fixes, /code-reviewer re-reviews)
↓
/qa-engineer → Full QA testing → bug-report.md
↓
(If bugs found, repeat fix → review → test loop)
↓
/devops-engineer & /tech-writer (in parallel)
  → DEPLOYMENT.md + CI/CD + docs
↓
Deployed & documented ✅
```

### Option 2: Use idk_it Agent (Recommended)

```
User: "I want to build a user management API"

→ idk_it detects "new" project
→ idk_it spawns req-engineer for interview
→ idk_it spawns sw-architect with requirements.md
→ idk_it spawns proj-manager with plan.md
→ ... and so on through the full pipeline
→ idk_it handles checkpoints and error recovery
```

---

## Quality Guarantees

1. **Requirements** — Validated by domain research (WebSearch)
2. **Architecture** — SAST tools verify no security/quality gaps
3. **Design** — Accessibility & responsiveness tested
4. **Implementation** — Unit tests required, builds verified
5. **Code Quality** — Linters, SAST, architectural compliance checked
6. **Testing** — Project-type appropriate testing with tool evidence
7. **Documentation** — Examples verified against live code
8. **Deployment** — CI/CD pipelines tested, rollback verified

---

## When You're Ready to Build

The system is **idle and ready**. When you want to create something:

1. Tell the user which skill(s) to invoke
2. Or invoke the idk_it orchestrator with your project idea
3. Follow the multi-round requirements gathering process
4. The system will guide you through architecture → implementation → QA → deployment

---

## Technical Stack Supported

- **Languages**: JavaScript/TypeScript, Python, Go, Java, Rust, and others
- **Frameworks**: React, Vue, Next.js, Express, FastAPI, Django, Spring Boot, etc.
- **Databases**: PostgreSQL, MySQL, MongoDB, DynamoDB, etc.
- **Cloud**: AWS, GCP, Azure, self-hosted
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Containerization**: Docker, Docker Compose, Kubernetes (optional)
- **Testing**: Jest, Vitest, Pytest, Go test, JUnit
- **Security**: Semgrep, Bandit, npm audit, pip-audit

---

## Next Step

When you want to build something, say **"I'm ready to build"** or describe your idea, and the system will guide you through structured requirements gathering and then automate the entire development pipeline with tool-based verification at every step.
