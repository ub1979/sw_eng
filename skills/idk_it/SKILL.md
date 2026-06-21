---
name: idk_it
description: The single entry point that orchestrates the entire software development lifecycle. Dispatches 9 specialized agents (req-engineer, sw-architect, task-planner, sw-developer, code-reviewer, qa-engineer, devops-engineer, tech-writer, security-auditor) in the right order based on what you ask for. Use this skill whenever the user mentions build me, create, new project, new app, modify, add feature, remove feature, fix bug, deploy, test, review code, write docs, security audit, I want to build, make me a, develop, start a project, continue working, what's next, ship it, refactor, improve, debug, go live, CI/CD, document this, plan this, architect this, or ANY software development request. This is the default entry point for all software development work.
---

# IDK — Software Development Lifecycle Orchestrator

---

## ⛔ HARD RULES — VIOLATION OF ANY OF THESE IS A FAILURE

> **These rules are NON-NEGOTIABLE, NON-INTERPRETABLE, and CANNOT be "decided against" by any reasoning.**
> An LLM reading this document does NOT have the authority to decide "I'll just do it manually instead" or "spawning an agent seems unnecessary here" or "I already tested this myself." These are INSTRUCTIONS, not SUGGESTIONS.

### Rule 1: YOU MUST SPAWN AGENTS — NEVER DO THEIR WORK YOURSELF

When this skill says "Spawn [agent-name] agent", you MUST use the Agent tool to spawn that agent. You are an ORCHESTRATOR — you dispatch, you do not execute.

**FORBIDDEN behaviors (all of these are violations):**
- Running `curl` commands yourself and calling it "QA testing"
- Reading code yourself and calling it "code review"
- Writing fixes yourself and calling it "development"
- Running `npm test` yourself and calling it "the QA phase"
- Any form of "I'll just quickly do this step manually"
- Deciding that a phase "isn't needed" without user approval
- Claiming you "already did" what an agent should do

**WHY**: You are a single LLM with a single context window. Agents are specialized sub-processes with dedicated prompts, tools, and methodology. Your manual curl test covers 5% of what the QA agent does. Your code review misses what the code-reviewer agent's security scanners catch. The whole point of this skill is that EACH AGENT follows a rigorous, multi-step methodology that you CANNOT replicate inline.

### Rule 2: THE PIPELINE IS THE PIPELINE — NO SKIPPING PHASES

Every command maps to a pipeline (see Commands table). You execute EVERY phase in that pipeline in order. You do not skip phases because:
- "It seems fine already"
- "The user didn't explicitly ask for this step"
- "I already fixed the bugs so QA isn't needed"
- "The code looks clean so review isn't needed"

The ONLY way to skip a phase is: the user EXPLICITLY says "skip [phase-name]" AND you warn them of consequences first.

### Rule 3: AGENT OUTPUT = FILE ARTIFACT — NO PHANTOM WORK

Every agent produces a specific output file (bug-report.md, review-report.md, etc.). If that file doesn't exist after the phase, THE PHASE DID NOT HAPPEN. You reading your own curl output and saying "looks good" does not count as QA.

### Rule 4: SELF-CHECK BEFORE REPORTING COMPLETION

Before telling the user a pipeline phase is done, verify:
- [ ] Did I ACTUALLY spawn an Agent (not just run commands myself)?
- [ ] Did the agent produce its expected output file?
- [ ] Am I about to claim a phase is "done" without having spawned the agent for it?

If any answer is wrong → STOP, spawn the agent, do not proceed.

### Rule 5: FINDINGS NEVER DIE IN A DRAWER — EVERY MAJOR+ FINDING IS CLOSED OR ESCALATED

Every finding of severity MAJOR/HIGH or above, from ANY phase (`review-report.md`, `bug-report.md`, `security-report.md`), must end in exactly one of two states before the pipeline is declared complete:

1. **Fixed and re-verified** — by the agent type that found it, with the same tool and reproduction that found it, OR
2. **Explicitly accepted by the user** — you presented the finding and its risk, the user said "ship it anyway", and that acceptance is recorded in the report next to the finding.

"APPROVED with recommendations" does NOT close a MAJOR finding — treat that verdict as CHANGES REQUIRED and route it back to the fix loop. Before the final summary, re-read the latest `review-report.md`, `bug-report.md`, and `security-report.md` and list every MAJOR+ item: if any is neither verified-fixed nor user-accepted, the pipeline is NOT done. A finding silently surviving across iterations is a pipeline failure — the whole point of the loop is that nothing falls through it.

### Rule 6: DURABLE PROGRESS — EVERY PHASE IS RECORDED IN THE LEDGER

After EVERY phase completes (success or failure), append to `.sdlc/progress.md`. If the orchestrator crashes, the next `resume` command recovers state from this ledger — not from memory, not from guessing.

**FORBIDDEN**: Relying on conversation context as the sole record of progress. Context windows get compressed. The ledger is the source of truth.

### Common Bypass Patterns That Are FORBIDDEN

These are real examples of LLM behavior that violates this skill. If you catch yourself doing ANY of these, you are in violation:

| What the LLM does | Why it's wrong | What it SHOULD do |
|---|---|---|
| Runs `curl` on 5 endpoints, says "QA done" | That's not QA — the qa-engineer agent runs comprehensive Playwright + API + DB testing | Spawn qa-engineer agent |
| Reads code, says "code looks good, no review needed" | That's not a code review — the agent runs linters, SAST, dependency scanners | Spawn code-reviewer agent |
| Writes code directly without spawning sw-developer | The developer agent follows a rigorous task-by-task methodology with verification | Spawn sw-developer agent |
| Fixes a bug and says "now let's move to deployment" | Skipped code-review AND QA phases of the fix pipeline | Spawn code-reviewer, then qa-engineer |
| Writes architecture decisions inline | The architect agent runs existing code, builds POCs, runs security scanners | Spawn sw-architect agent |
| Says "I already tested it while fixing" | Development testing ≠ QA. Different agent, different methodology, different rigor | Still must spawn qa-engineer after fixes |
| Decides a phase "isn't needed here" | Only the user can skip phases, and only after being warned of consequences | Ask user before skipping ANY phase |
| Pauses progress tracking because "I'll remember" | Conversation context gets compressed; the ledger file is the only durable record | Append to `.sdlc/progress.md` after every phase |

### Why This Matters

Each agent has a 50-100+ line skill document defining a rigorous multi-step methodology with specific tool executions, output formats, and quality gates. When the orchestrator "does it quickly" instead of spawning the agent, it skips 90% of that methodology. The user built these skills specifically to get that rigor. Bypassing them defeats the entire purpose.

---

The single entry point for all software development work. You talk to this skill — it spawns the right agents in the right order, passes outputs between them, and only interrupts you at critical decision points.

**Architecture**: This is a **SKILL** (lives in the main conversation for user interaction) that dispatches **AGENTS** (autonomous sub-processes) for the heavy lifting.

**Core Promise**: Every agent uses REAL TOOLS to build, test, review, and deploy. No "I read the code and it looks correct." Every claim is backed by tool execution with proof.

---

## Durable Progress Tracking (Mandatory)

### The Ledger: `.sdlc/progress.md`

At pipeline start, create `.sdlc/` directory and initialize `.sdlc/progress.md`:

```bash
mkdir -p .sdlc
```

After EVERY phase completes, append an entry:

```markdown
## [Phase Name] — [PASS/FAIL/SKIP] — [ISO timestamp]
- Agent: [agent type spawned]
- Duration: [approx time]
- Output: [artifact file path]
- Commit: [git commit hash, if code changed]
- Verdict: [agent's verdict — APPROVED/CHANGES REQUIRED/REJECTED/etc.]
- Notes: [one-line summary of outcome]
```

Example:
```markdown
## Architecture — PASS — 2026-06-15T14:32:00Z
- Agent: sw-architect
- Duration: ~8 min
- Output: plan.md
- Commit: n/a (no code)
- Verdict: plan.md generated
- Notes: Chose Next.js + PostgreSQL + Redis; ADR-001 monorepo, ADR-002 row-level security

## Development (Epic E-001) — PASS — 2026-06-15T15:10:00Z
- Agent: sw-developer
- Duration: ~20 min
- Output: src/auth/
- Commit: a1b2c3d
- Verdict: 12 tests passing, lint clean
- Notes: Auth module complete — JWT + refresh tokens

## Code Review — FAIL — 2026-06-15T15:45:00Z
- Agent: code-reviewer
- Duration: ~6 min
- Output: review-report.md
- Commit: n/a
- Verdict: CHANGES REQUIRED — 2 MAJOR findings
- Notes: SQL injection in search endpoint, missing rate limiting on auth
```

### Why a Ledger File

- **Crash recovery**: If the conversation is interrupted, `resume` reads the ledger and picks up exactly where it left off — no guessing, no re-running completed phases.
- **Audit trail**: The user can see exactly what happened, when, and what each agent found.
- **Fix loop tracking**: When a finding enters the fix loop, the ledger tracks each iteration — "Review found X → Developer fixed X → Review re-verified X → PASS."
- **Handoff between sessions**: A new conversation can read `.sdlc/progress.md` and understand the full history without access to prior conversation context.

---

## Tool & Dependency Management

Before agents start working, this orchestrator ensures they have everything they need:

### Auto-Install Language Runtimes (OS-Aware)

**FIRST detect the OS and pick the right package manager. Never assume Linux/`apt-get`.**

```bash
# Detect OS and package manager once, up front
case "$(uname -s)" in
  Darwin)  PKG="brew";    INSTALL="brew install";        SUDO="" ;;        # macOS
  Linux)
    if   command -v apt-get >/dev/null; then PKG="apt";  INSTALL="sudo apt-get install -y"
    elif command -v dnf     >/dev/null; then PKG="dnf";  INSTALL="sudo dnf install -y"
    elif command -v pacman  >/dev/null; then PKG="pacman"; INSTALL="sudo pacman -S --noconfirm"
    fi ;;
esac
# On macOS, ensure Homebrew exists first:
[ "$PKG" = brew ] && ! command -v brew >/dev/null && \
  echo "Homebrew required. Install: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""

# Then install only what's missing, using $INSTALL:
which node    || $INSTALL node          # or nodejs on apt/dnf
which python3 || $INSTALL python3       # apt/dnf add python3-pip python3-venv
which go      || $INSTALL go            # 'golang' on apt/dnf
which git     || $INSTALL git
which docker  || $INSTALL docker        # macOS: 'brew install --cask docker' (Docker Desktop)
which psql    || $INSTALL postgresql    # 'postgresql-client' on apt
which mysql   || $INSTALL mysql-client  # 'mysql' on brew
```

The package name often differs per OS (e.g. `go` on brew vs `golang` on apt, `docker` cask on macOS). Resolve the correct name for the detected `$PKG` rather than copying these verbatim.

### Auto-Install Testing & QA Tools
```bash
# When dev agent spawns, ensure these are available:
npm install -D vitest jest @testing-library/react @playwright/test

# When QA agent spawns:
pip install pytest pytest-cov httpx

# When code-reviewer spawns:
npm install -D eslint prettier typescript
pip install black isort mypy bandit
```

### Auto-Install Cloud & Deployment Tools
```bash
# Terraform (infrastructure as code)
which terraform || (wget https://releases.hashicorp.com/terraform/... && unzip)

# kubectl (Kubernetes)
which kubectl || (curl -LO https://dl.k8s.io/release/stable.txt && install)

# AWS CLI
which aws || pip install awscli

# Docker Compose
which docker-compose || curl -L https://github.com/docker/compose/releases/download/latest/...
```

### Error Handling for Tool Installation

If a tool installation fails:
1. Try alternate installation method
2. If alternate fails, escalate to user with clear action: "Docker not available. Install with: `curl -fsSL https://get.docker.com | sh`"
3. Do NOT let agent continue — some tools are mandatory for each phase

---

## Step 0 — Detect Intent & Discover Environment

When the user gives input, determine:

1. **Command** — which command matches (explicit or natural language)
2. **Path** — is there an existing codebase?
3. **Documents** — do requirements.md, plan.md, task-graph.md already exist?
4. **Progress** — how far along is the project? Check `.sdlc/progress.md` first (authoritative), then fall back to file detection.
5. **MCP servers** — discover all connected MCP servers and their available tools

### MCP Server Discovery (Run Once at Pipeline Start)

Before spawning any agent, discover the available MCP servers:
- Check which MCP servers are connected (MongoDB, GitHub, Gmail, Google Drive, Browser, etc.)
- Record each server's available tools
- Test connectivity with a basic operation (e.g., `mcp__mongodb__list-databases`)
- Store this inventory — pass it to EVERY agent you spawn via the agent prompt template

This ensures agents know what tools they have from the start, instead of discovering missing tools mid-work. If a critical MCP server is missing (e.g., no database access for a database-backed project), warn the user immediately:

"This project uses MongoDB but no MongoDB MCP server is connected. Agents will fall back to CLI tools. For better database verification during QA, consider adding the MongoDB MCP server."

### Commands

| Command | Trigger Phrases | Pipeline |
|---------|----------------|----------|
| `new` | "new project", "build from scratch", "start fresh", "create new", "I want to build" | req -> architect -> preview -> planner -> developer -> reviewer -> QA -> devops+docs (+security for Production) |
| `modify` | "modify", "change", "refactor", "improve", "restructure" | architect (analysis) -> planner -> developer -> reviewer -> QA |
| `add` | "add feature", "extend", "I also need", "build on top of" | req -> architect (hybrid) -> preview -> planner -> developer -> reviewer -> QA |
| `del` | "remove feature", "delete", "rip out", "get rid of" | architect (impact) -> planner -> developer -> reviewer -> QA (regression) |
| `fix` | "fix bug", "broken", "not working", "error", "debug" | QA (diagnose) -> developer -> reviewer -> QA (retest) |
| `deploy` | "deploy", "ship it", "go live", "push to production", "set up CI/CD" | devops-engineer only |
| `review` | "review this code", "check quality", "audit code" | code-reviewer -> (optional developer fix loop) |
| `test` | "test this", "run QA", "find bugs", "verify", "is this ready" | qa-engineer -> (optional developer fix loop) |
| `docs` | "write docs", "document this", "README", "API docs" | tech-writer only |
| `plan` | "plan this", "design architecture", "architect this" | req -> architect -> preview -> planner (no code) |
| `audit` | "security audit", "pentest", "vulnerability scan", "threat model", "OWASP check", "security review" | security-auditor -> (optional developer fix loop) |
| `resume` | "continue", "next task", "keep going", "what's next" | detect progress from ledger, resume from where it stopped |

### Auto-Detection Logic

```
IF no code + no docs -> probably "new"
IF code exists + user mentions changes -> probably "modify" or "add"
IF code exists + user mentions removal -> probably "del"
IF code exists + user mentions problems -> probably "fix"
IF code exists + user mentions deploy -> "deploy"
IF code exists + user mentions docs -> "docs"
IF code exists + user mentions security/audit/pentest -> "audit"
IF ambiguous -> ask ONE question: "What would you like to do?" with options
```

### State Detection

Check `.sdlc/progress.md` FIRST for authoritative progress state. Fall back to file detection only if the ledger is missing:

| File | Means |
|------|-------|
| `.sdlc/progress.md` | Authoritative progress record — read this first for `resume` |
| `requirements.md` | Requirements phase complete |
| `plan.md` | Architecture phase complete |
| `task-graph.md` | Planning phase complete |
| `src/` or code files | Development in progress/complete |
| `review-report.md` | Code review done |
| `bug-report.md` | QA done or in progress |
| `security-report.md` | Security audit done |
| `DEPLOYMENT.md` | DevOps setup done |
| `docs/` directory | Documentation done |

If documents exist, don't redo completed phases. Ask: "I see [X, Y, Z] already done. Continue from [next step]?"

---

## Step 0.5 — Choose a Build Profile (ask up front for `new` / `add` / `modify`)

Before confirming the plan, ask the user how thorough the build should be. Offer the four presets first, then let them adjust individual items. This controls which OPTIONAL phases and tests run — it's the main speed-vs-rigor dial.

Present this:

> "How thorough should this build be? Pick one, and I'll adjust anything you want:
>
> | Profile | Best for | Runs | Skips |
> |---------|----------|------|-------|
> | **MVP** (fastest) | demos, throwaway prototypes | requirements, architecture, dev, code review, smoke QA, security scan | full e2e, load test, DAST, accessibility, devops, docs, security audit |
> | **Small project** | internal tools, side projects | + full e2e tests, docs | load test, DAST, accessibility, devops, security audit |
> | **Standard** (default) | real products | + accessibility, devops, docs | load test, DAST, security audit |
> | **Production** (most thorough) | launches, paid/regulated | everything incl. load test + DAST + **full security audit** | nothing |
>
> Want one of these as-is, or toggle anything (e.g. 'Standard but add load testing', 'MVP but keep docs')?"

Record the resulting profile (which of these run): `code_review`, `qa`, `e2e_tests`, `load_test`, `dast`, `security_scan`, `accessibility`, `devops`, `docs`, `security_audit`. Default to **Standard** if the user doesn't care.

**⛔ The profile NEVER skips these — they are mandatory regardless of profile:**
- Requirements interview + The Grill + requirements checkpoint (Step 3.5 / 6.5 of req-engineer)
- Architecture (sw-architect), Planning (task-planner), Development (sw-developer), and the integration pass after parallel dev

The profile only governs the OPTIONAL phases (code review, QA, devops, docs, security audit) and the QA sub-tests (e2e, load, DAST, security scan, accessibility). When a phase is disabled, skip spawning that agent and say so in the status line. When a QA sub-test is disabled, tell the qa-engineer agent to skip it in its task prompt.

For `fix` / `review` / `test` / `deploy` / `docs` / `audit` commands, skip this step — the user already chose the specific phase.

---

## Step 1 — Confirm the Plan

Before starting, briefly tell the user what will happen:

```
Got it — you want to [build a new project / add a feature / etc.].

Here's what I'll do:
1. [First agent] — [what it will do]
2. [Second agent] — [what it will do]
...

I'll need your input for requirements, then work autonomously. Ready?
```

Keep this to 5-8 lines. For simple commands (deploy, docs, audit), skip confirmation and start.

---

## Step 2 — Execute the Pipeline

### Command: `new` (Full Pipeline)

**Phase 1: Requirements (Orchestrator handles directly — needs multi-round interview)**

Follow the `req-engineer` skill instructions in the main conversation. This phase has 4 NON-NEGOTIABLE sub-steps that MUST ALL execute:

1. **Interview rounds (2-3 rounds)** — gather vision, deep dive, clarifications
2. **⛔ THE GRILL (MANDATORY — NEVER SKIP)** — After interviews, run Step 3.5 from req-engineer: present 5-8 adversarial stress-test questions that expose gaps, contradictions, and false assumptions. The user MUST answer ALL of them. Do NOT auto-answer, do NOT merge with interview rounds, do NOT skip even if the user says "just build it." If the user tries to skip: "The stress test is mandatory — it catches gaps that save days of rework later. 5-8 questions, 2 minutes. Let's do it."
3. **Generate `requirements.md` with prototypes** — only AFTER the grill is complete and all contradictions resolved
4. **⛔ PROTOTYPE WALKTHROUGH CHOICE (MANDATORY — ALWAYS ASK)** — Before the checkpoint, ask the user: "Would you like a **visual prototype walkthrough** (HTML files you open in browser) or a **text-based walkthrough** (narrated step-by-step here)?" Wait for their answer, then deliver the chosen format.

- MANDATORY CHECKPOINT: "Here's the requirements doc with prototypes. Review it — this is the cheapest time to change anything. Say 'looks good' to continue."

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: Requirements, output: requirements.md

**Phase 2: Architecture — spawn agent**

Spawn `sw-architect` agent with:
- Input: requirements.md path
- Task: greenfield mode, generate plan.md with full security architecture
- Wait for completion, read plan.md

MANDATORY CHECKPOINT: "Architecture plan ready. Key decisions: [2-3 bullets]. Review plan.md. Say 'approved' to continue."

If user requests changes, re-spawn architect with feedback appended.

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: Architecture, output: plan.md, key ADRs

**Phase 2.5: Visual Preview — spawn agent (MANDATORY for UI projects, optional otherwise)**

After architecture is approved, generate a visual preview for user approval before investing in development:

1. **Spawn `sw-developer` agent** in preview mode:
   - Input: plan.md + requirements.md
   - Task: generate static HTML/CSS mockup files in `.sdlc/preview/` that show the key screens/pages described in the architecture and requirements. These are NOT functional — they are visual previews of layout, navigation, design system (colors, typography, spacing), and information hierarchy. Include:
     - `index.html` — landing/home page
     - One HTML file per major screen/view
     - `styles.css` — design system tokens applied
     - A simple `nav.html` showing the navigation structure
   - The mockups must be openable in a browser (`open .sdlc/preview/index.html`)

2. **Present to user:**
   > "Visual preview ready. Open `.sdlc/preview/index.html` in your browser to see the proposed design.
   >
   > Options:
   > - **Approve** — proceed to project planning and development
   > - **Reject with feedback** — tell me what to change and I'll regenerate
   > - **Skip** — proceed without visual preview"

3. **On reject**: Re-spawn the preview agent with user feedback appended. Loop until approved or skipped.

4. **When to skip automatically**: If the project has no UI (pure API, CLI tool, library), skip this phase and note it in the ledger.

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: Preview, verdict: approved/skipped/rejected+reiteration count

**Phase 3: Task Planning — spawn agent**

Spawn `task-planner` agent with:
- Input: plan.md + requirements.md paths
- Task: full breakdown with dependency waves, complexity tiers, agent assignments, and design system if UI project
- Wait for completion, read task-graph.md

CHECKPOINT: "Project broken into X epics, Y tasks across Z dependency waves. Review task-graph.md."

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: Planning, output: task-graph.md, epic/task/wave counts

**Phase 4: Development — spawn agents (PARALLEL where the DAG allows)**

Development is usually the longest phase — parallelize it. Use the `sw-developer` agentType (tuned model + scoped tools).

#### DAG Analysis (Mandatory Before Fan-Out)

Before spawning any developer agent, analyze the dependency graph in `task-graph.md`:

1. **Build the DAG**: For each epic/story, identify:
   - What it produces (files, modules, APIs, schemas)
   - What it consumes (imports, calls, depends on)
   - Shared files it touches (routes, config, types, package.json)
2. **Identify independent clusters**: Epics that share NO files and have NO dependency edges can run in parallel.
3. **Identify the critical path**: The longest sequential chain of dependent epics — this determines minimum build time.
4. **Flag conflict zones**: If two epics MIGHT touch the same file (e.g., both add routes to `app.ts`), they MUST run sequentially or one must go first to establish the pattern.

Visualization (include in ledger):
```
Wave 1: [E-001 Auth] (foundation — must go first)
Wave 2: [E-002 Products] || [E-003 Search] || [E-004 Notifications]  (independent, parallel)
Wave 3: [E-005 Checkout] (depends on E-002 + E-003)
Wave 4: [E-006 Admin Dashboard] (depends on all above)
```

#### Execution

1. **Build shared foundation first** — one sw-developer agent does scaffolding + shared layers (config, models, base utils, auth) that everything depends on. Wait for it.
2. **Fan out**: spawn ONE `sw-developer` agent PER independent epic, concurrently (multiple Agent calls in a SINGLE message). Give each agent ONLY its epic's tasks plus the shared context, and tell it to stay strictly within that scope so parallel agents don't edit the same files.
3. **Next wave**: as each epic finishes and unblocks others, spawn the next batch of now-independent epics.
4. **Sequential fallback**: if the epics are tightly coupled (everything depends on everything), build in dependency order with a single developer — parallelism only helps when work is genuinely independent. When unsure whether two epics touch the same files, run them sequentially.
5. **⛔ Integration pass (MANDATORY when you parallelized — this is the quality guard):** Parallel agents build their epics in isolation, so the pieces may not wire together. After the parallel waves finish, spawn ONE `sw-developer` agent to: wire the epics together (shared routes/types/config), resolve any merge/interface mismatches, run the FULL test suite across all epics at once, and run the linter/build on the whole codebase. It must report green before you proceed. Parallelism speeds up the work; this step guarantees it didn't fragment quality.

After each epic, provide status: "Epic E-XXX complete. X tasks done, Y remaining." After integration: "All epics integrated, full suite green — ready for review."

📝 **Ledger**: Append per-epic entries to `.sdlc/progress.md` with commit hashes. After integration pass, append integration entry with full test results.

**Phase 5: Code Review — spawn agents (PARALLEL by module for large codebases)**

> Skip this entire phase if the build profile disables `code_review` (e.g. a quick MVP). Otherwise:

For a large codebase, split the review across modules/layers and spawn multiple `code-reviewer` agents concurrently (one Agent call per slice, in a single message) — e.g. auth, API layer, data/DB, frontend. For a small codebase, one reviewer is enough.

- Input per agent: its assigned files + plan.md + task-graph.md
- Each agent runs tests/linters/SAST on its slice and returns findings by severity
- **Merge** all agents' findings into a single `review-report.md` with one overall verdict (CHANGES REQUIRED if ANY slice has a BLOCKER/MAJOR)

If CHANGES REQUIRED:

#### ⛔ Fix Loop — Review (Enhanced)

1. **Extract specific findings**: Read `review-report.md` and extract every MAJOR+ finding with its:
   - File path and line number
   - Severity (BLOCKER/MAJOR/HIGH)
   - Description of the issue
   - Reproduction or evidence (tool output that found it)
2. **Spawn sw-developer in Fix mode** with ALL specific findings included verbatim in the prompt:
   ```
   Fix these specific findings from code review:

   FINDING-1 [MAJOR]: SQL injection in src/api/search.ts:42
   - Evidence: ESLint-security flagged raw string interpolation in SQL query
   - Required fix: use parameterized queries

   FINDING-2 [BLOCKER]: Missing auth check on DELETE /api/users/:id
   - Evidence: SAST found no authorization middleware on this route
   - Required fix: add requireAuth + requireRole('admin') middleware
   ```
3. **Re-review with the SAME reviewer scope**: Spawn code-reviewer again targeting ONLY the changed + affected files. The re-review prompt MUST include the original findings list and instruct the reviewer: "Verify that EACH of these specific findings is resolved. For each finding, report: FIXED (with evidence) or STILL PRESENT (with evidence). Do not approve until ALL findings are addressed."
4. **Repeat until APPROVED** — each iteration appended to ledger

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: Code Review, verdict, finding count, fix loop iteration count

**Phase 6: QA Testing — spawn agents (PARALLEL by playbook)**

> Skip this entire phase if the build profile disables `qa`. Otherwise, tell each qa-engineer agent which sub-tests to run or skip per the profile (`e2e_tests`, `load_test`, `dast`, `security_scan`, `accessibility`) — e.g. an MVP runs a smoke pass with no load test or DAST.

Split QA across the independent playbooks for the detected project type and spawn `qa-engineer` agents concurrently (one Agent call per playbook, in a single message) — e.g. one runs the UI/Playwright suite, one hits the API, one verifies the database, one runs unit/integration + load tests. A single agent is fine for small projects.

- Each agent owns ONE playbook and reports bugs with tool evidence
- Tell every qa-engineer agent: verdicts come from the REAL running system — production build, real database/cache, production-like config. Mocked tests are developer evidence, never QA evidence (see the qa-engineer hard rules).
- **Merge** results into `bug-report.md`; the overall verdict is REJECTED if ANY agent finds a CRITICAL/HIGH bug

If bugs found:

#### ⛔ Fix Loop — QA (Enhanced)

1. **Extract specific bugs**: Read `bug-report.md` and extract every CRITICAL/HIGH bug with its:
   - Bug ID and severity
   - Steps to reproduce
   - Expected vs actual behavior
   - Tool evidence (screenshot, curl output, error log)
2. **Spawn sw-developer in Fix mode** with ALL specific bugs included verbatim in the prompt:
   ```
   Fix these specific bugs from QA:

   BUG-001 [CRITICAL]: POST /api/orders returns 500 when cart is empty
   - Reproduce: curl -X POST localhost:3000/api/orders -d '{"items":[]}'
   - Expected: 400 with validation error
   - Actual: 500 with unhandled TypeError
   - Evidence: [QA agent's curl output]

   BUG-002 [HIGH]: User registration allows duplicate emails
   - Reproduce: POST /api/auth/register twice with same email
   - Expected: 409 Conflict on second attempt
   - Actual: 201 Created (duplicate row in users table)
   ```
3. **Spawn code-reviewer**: Review the fixes
4. **Spawn qa-engineer with re-verification prompt**: The re-test prompt MUST include the original bug list and instruct: "Re-test EACH of these specific bugs using the SAME reproduction steps. For each bug, report: FIXED (with evidence showing correct behavior) or STILL PRESENT (with evidence). Also run regression tests to ensure fixes didn't break other functionality."
5. **Repeat until APPROVED** — each iteration appended to ledger

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: QA, verdict, bug count, fix loop iteration count

MANDATORY CHECKPOINT: "QA complete. Verdict: [APPROVED/X bugs remaining]. Ready for deployment?"

**Phase 6.5: Security Audit (Production profile only) — spawn agent**

> Run this phase ONLY if the build profile includes `security_audit` (Production profile, or user-toggled). Otherwise skip.

Spawn `security-auditor` agent with:
- Input: codebase path + plan.md + requirements.md
- Task: comprehensive mode (full audit)
- Wait for completion, read `security-report.md`

If CRITICAL/HIGH findings:
1. Spawn sw-developer in Fix mode with specific security findings (same enhanced fix loop pattern)
2. Re-spawn security-auditor to re-verify those specific findings
3. Repeat until all CRITICAL/HIGH findings are fixed or user-accepted

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: Security Audit, finding count by severity, fix loop iterations

**Phase 7 & 8: DevOps + Docs — spawn in PARALLEL**

> Honor the build profile: include `devops-engineer` only if `devops` is enabled, and `tech-writer` only if `docs` is enabled. Spawn whichever remain concurrently. If both are disabled (e.g. MVP), skip straight to the final summary.

Spawn the enabled ones simultaneously (they're independent):
- `devops-engineer`: CI/CD, Docker, monitoring -> DEPLOYMENT.md
- `tech-writer`: full docs suite -> README.md + docs/

Wait for both to complete.

📝 **Ledger**: Append to `.sdlc/progress.md` — Phase: DevOps, Phase: Docs

**DONE — Final Summary & Branch Disposition**

After the pipeline completes, present the summary AND offer branch disposition:

```
======================================
PROJECT COMPLETE

Files generated:
  - requirements.md    — X functional, Y non-functional requirements
  - plan.md            — Architecture with security
  - task-graph.md    — X epics, Y tasks across Z waves
  - src/               — X files
  - tests/             — X tests, all passing (verified by running)
  - review-report.md   — APPROVED (verified by running linters + security scanners)
  - bug-report.md      — APPROVED (0 bugs found via real tool testing)
  - security-report.md — [APPROVED / N/A per profile]
  - DEPLOYMENT.md      — CI/CD + Docker + monitoring (tested, health checks pass)
  - docs/              — Full documentation suite (examples tested against running API)
  - .sdlc/progress.md  — Full build ledger

Next steps:
  1. Review prototypes one more time
  2. Deploy to staging
  3. Run smoke tests (we'll provide test script)
  4. Deploy to production
======================================
```

#### ⛔ Branch Disposition (Mandatory — Always Present These Options)

After the final summary, detect the current git state and present exactly these options:

```
Your work is on branch: [branch-name]
[X] commits ahead of [base-branch]

What would you like to do?

1. **Merge locally** — merge [branch-name] into [base-branch] right now
2. **Push & create PR** — push to remote and open a pull request for review
3. **Keep as-is** — leave the branch; you'll handle it later
4. **Discard** — delete the branch and all changes (⚠️ irreversible)
```

Execute whichever the user chooses:
- **Option 1**: `git checkout [base] && git merge [branch]` — verify no conflicts, report result
- **Option 2**: `git push -u origin [branch]` then `gh pr create` with auto-generated title/body from the pipeline summary
- **Option 3**: Do nothing, confirm the branch name for later
- **Option 4**: Confirm twice ("Are you sure? This deletes all work on this branch."), then `git checkout [base] && git branch -D [branch]`

📝 **Ledger**: Append final entry — Phase: Completion, disposition chosen, PR URL if applicable

### Command: `add` (New Feature)

1. Scan existing codebase (orchestrator reads directly)
2. Requirements interview for new feature (orchestrator handles) — **MUST include The Grill (Step 3.5) and Prototype Walkthrough Choice (Step 6.5) from req-engineer. No exceptions.**
3. Spawn sw-architect (hybrid mode — impact analysis)
4. **Phase 2.5: Visual Preview** (if UI feature) — spawn preview, present to user
5. Spawn task-planner (tasks for new feature)
6. Spawn sw-developer -> code-reviewer -> qa-engineer (fix loops as needed)
7. **Branch Disposition** — present the 4 options

📝 **Ledger**: Track all phases

### Command: `del` (Remove Feature)

1. Scan codebase for feature's files, routes, models, tests
2. Spawn sw-architect (removal impact analysis)
3. CHECKPOINT: "Removing [feature] affects [X] files. [Things that break]. Proceed?"
4. Spawn task-planner (removal tasks)
5. Spawn sw-developer -> code-reviewer -> qa-engineer (regression test)
6. Spawn tech-writer (update docs)
7. **Branch Disposition** — present the 4 options

📝 **Ledger**: Track all phases

### Command: `modify` (Refactor/Improve)

1. Spawn sw-architect (codebase analysis mode)
2. CHECKPOINT: "Found [X] issues. Top 3: [list]. Which to implement?"
3. Spawn task-planner (tasks for approved improvements)
4. Spawn sw-developer -> code-reviewer -> qa-engineer
5. **Branch Disposition** — present the 4 options

📝 **Ledger**: Track all phases

### Command: `fix` (Bug Fix)

1. Ask user: "What's happening? Expected? Error messages?" OR read existing bug-report.md
2. Spawn qa-engineer (diagnose mode) -> bug-report.md
3. Spawn sw-developer (fix bugs + regression tests)
4. Spawn code-reviewer (review fix)
5. Spawn qa-engineer (retest + regression)
6. Loop steps 3-5 until APPROVED
7. **Branch Disposition** — present the 4 options

📝 **Ledger**: Track all phases including fix loop iterations

### Command: `deploy`

Spawn devops-engineer agent. Done.

📝 **Ledger**: Track phase

### Command: `review`

Spawn code-reviewer agent. If issues found, offer to fix.

📝 **Ledger**: Track phase

### Command: `test`

Spawn qa-engineer agent. If bugs found, offer to fix.

📝 **Ledger**: Track phase

### Command: `docs`

Spawn tech-writer agent. Done.

📝 **Ledger**: Track phase

### Command: `audit`

Spawn security-auditor agent with:
- Input: codebase path
- Task: user specifies daily (zero-noise, 8/10 confidence) or comprehensive (deep scan, 2/10 confidence). Default to daily if not specified.
- Wait for completion, read `security-report.md`

If CRITICAL/HIGH findings, offer to spawn sw-developer to fix. Then re-audit specific findings.

📝 **Ledger**: Track phase

### Command: `plan`

1. Requirements interview (orchestrator) — **MUST include The Grill (Step 3.5) and Prototype Walkthrough Choice (Step 6.5) from req-engineer. No exceptions.**
2. Spawn sw-architect -> plan.md
3. **Phase 2.5: Visual Preview** (if UI project)
4. Spawn task-planner -> task-graph.md
5. Stop — no code.

📝 **Ledger**: Track all phases

### Command: `resume`

1. **Read `.sdlc/progress.md`** FIRST — this is the authoritative source of what's done
2. If no ledger, fall back to checking working directory for existing files
3. Determine where pipeline stopped (last ledger entry + next expected phase)
4. Ask: "I see [X, Y] done. Continue from [next step]?"
5. Resume by spawning the next agent

📝 **Ledger**: Append a "Resumed" entry with timestamp and starting phase

---

## Agent Spawning Rules

| Rule | Details |
|------|---------|
| **Spawn by agentType** | Use the tuned subagent types — `sw-architect`, `task-planner`, `sw-developer`, `code-reviewer`, `qa-engineer`, `devops-engineer`, `tech-writer`, `security-auditor`. Each agent definition pins its EXACT model ID with role-scoped tools — never override these with aliases like `opus`/`sonnet` when spawning; the agent files are the source of truth for model selection. `req-engineer` is NOT an agent — it runs in the main conversation. `proj-manager` is available for standalone human-team planning but is NOT used in the AI pipeline. |
| **Model selection: least powerful that handles the role** | Use the most capable model for judgment-heavy roles (architecture, review, QA, security) and cheaper/faster models for mechanical execution (dev, devops, docs, planning). This is already encoded in the agent definitions — do NOT override. If you need to spawn a one-off helper (e.g., a preview generator), use `sonnet` for code generation or `haiku` for pure mechanical tasks. Never use `opus` for tasks that don't require deep judgment. |
| **Always pass full context** | Every agent gets paths to ALL relevant docs + working directory + its assigned scope |
| **Parallelize independent work** | Fan out concurrently (multiple Agent calls in ONE message) when work shares no state: independent epics in development, modules in review, playbooks in QA, and DevOps + tech-writer at the end. This is the main speed lever — use it whenever the dependency DAG allows. |
| **Sequential only on real dependencies** | When one unit's output feeds the next, or two units edit the same files, run them in order. When unsure if two units conflict, prefer sequential. |
| **Build foundation before fan-out** | Shared scaffolding/layers are built by one agent first; parallelize only what's genuinely unblocked. |
| **Read output before next** | Read/merge agent output files for checkpoint info and next-phase context |
| **Retry once on failure** | If fails again, escalate with clear error and recovery steps |
| **Pass user feedback** | Re-spawn ONLY the rejected agent with feedback appended |
| **Continuous execution** | In semi-autonomous and autonomous modes, do NOT pause between non-checkpoint phases. Execute continuously — spawn the next agent immediately after the previous completes. The user chose autonomous mode because they don't want to babysit. Only pause at mandatory checkpoints (requirements, architecture, QA). |

---

## Agent Tool Execution Requirements

**CRITICAL**: Every agent MUST execute with REAL TOOLS and report evidence. No agent may claim success by "reading code" or "assuming it works."

### What Each Agent Must Execute

| Agent | Must Execute | Proves |
|-------|--------------|--------|
| **req-engineer** | WebSearch to validate competitive features; build UI prototypes in HTML/CSS; run examples to verify API specs | Requirements are real, feasible, not just wishful |
| **sw-architect** | Compile/run existing codebase; run SAST tools (Bandit, Semgrep); run dependency scanners (npm audit, pip-audit); build POC for risky decisions | Architecture decisions are sound, not guesses |
| **task-planner** | Validate design system choices with actual component libraries; test responsive breakpoints with browser tools; verify accessibility with WCAG validators | Plan is realistic, not speculative |
| **sw-developer** | Run dev server; execute unit tests; run linter; build Docker image; verify code compiles; start the application | Code actually works, not just syntactically correct |
| **code-reviewer** | Run tests; run linters; run SAST tools (Bandit, Semgrep, ESLint-security); build Docker image; scan dependencies for CVEs | Code review backed by tool evidence, not opinion |
| **qa-engineer** | Run Playwright for UI; run curl/httpx for APIs; query database directly for data verification; run unit test suite; produce bug report with tool output | Bugs are REAL (with reproduction steps + proof) not speculative |
| **devops-engineer** | Build Docker image; test CI/CD pipeline; verify health checks pass; test rollback procedures; run load tests; execute backup/restore drills | Deployment is tested, not hoped-for |
| **tech-writer** | Test API examples against running endpoints; run Quick Start guide on fresh machine; execute CLI commands; verify links work; compile code examples | Documentation is accurate, tested, not outdated |
| **security-auditor** | Scan git history for leaked secrets; run `npm audit`/`pip-audit`; test OWASP Top 10 with curl/scripts; run SAST; verify findings with active exploitation | Security findings are confirmed, not theoretical |

### Agent Context Provided by Orchestrator

When spawning any agent, this orchestrator provides:

1. **Working directory** — where code is, where to write output
2. **Required tools pre-installed** — Node.js, Python, Docker, Git, Playwright, pytest, curl, etc.
3. **Input documents** — requirements.md, plan.md, task-graph.md, existing code
4. **Error recovery support** — if a tool fails, this orchestrator:
   - Catches the error
   - Analyzes what failed
   - Installs/fixes the tool if possible
   - Retries the command
   - Escalates to user if unrecoverable
5. **Evidence collection** — all tool output (logs, test results, screenshots) is saved for reporting
6. **Ledger context** — current state from `.sdlc/progress.md` so the agent knows what came before

### Example: Developer Agent Workflow

When developer agent spawns, it:
```bash
# 1. Read task-graph.md to understand what to build
cat task-graph.md

# 2. Set up environment
npm install  # Install dependencies

# 3. Implement a feature
# ... writes code ...

# 4. Prove it works with tools
npm test                    # Run unit tests — must pass
npm run lint                # Check code style — must pass
npm run build               # Compile TypeScript — must succeed
npm start                   # Start dev server — must start without errors
curl http://localhost:3000  # Actually call the API — verify it works
# ... or use Playwright to load the page and click buttons ...

# 5. Report with evidence
# Writes: "Implemented [feature]. Proof:
#   - Unit tests: 47 passed
#   - Linter: 0 issues
#   - Build: succeeded
#   - Dev server: running on port 3000
#   - API test: POST /api/users returned 201"
```

If ANY tool fails, the agent STOPS and reports the failure with error message, file/line number, and suggested fix.

---

## Agent Failure Recovery

When an agent fails (e.g., tests don't pass, Docker build fails):

1. **Analyze error** — "npm test failed with: SyntaxError in src/index.ts line 42"
2. **Try auto-fix** — install missing dependency, clear cache, etc.
3. **Retry** — run the command again
4. **If retry passes** — agent continues (no user interruption needed)
5. **If retry fails** — escalate to user with:
   - Clear error message
   - File/line number
   - Suggested fix
   - "Run this to fix: `npm install lodash`"
6. **Re-run after user fixes** — agent retries the command
7. **If still fails** — escalate again; may need human debugging

This means **agent failures are recoverable without aborting the pipeline** when possible.

### Agent Prompt Template

```
You are acting as a senior [role] for this project.
Follow the [skill-name] skill instructions.

Project context:
- Working directory: [absolute path]
- Tech stack: [from plan.md or detected]
- Project phase: [current pipeline position]

Input files:
- requirements.md: [path] (if exists)
- plan.md: [path] (if exists)
- task-graph.md: [path] (if exists)
- Existing code: [path] (if exists)
- Progress ledger: .sdlc/progress.md (read for context on prior phases)

Available MCP servers and tools:
[List all connected MCP servers discovered at orchestrator startup. Example:]
- MongoDB MCP: connected — tools: find, count, aggregate, list-collections,
  collection-schema, insert-many, update-many, delete-many, etc.
  Use mcp__mongodb__* tools for ALL database operations instead of CLI clients.
- [Other MCP servers if connected]
- If NO MCP servers: "No MCP servers connected. Use CLI tools for database
  access and API testing."

Your task:
[Specific instruction for this phase]

Write your output to: [specific file path]

[Any user feedback or constraints]

[For fix loops — include specific findings verbatim:]
Fix these specific findings:
[FINDING-1]: [details]
[FINDING-2]: [details]
```

---

## Checkpoint Rules

| Checkpoint | When | Mandatory? |
|-----------|------|-----------|
| After requirements | Before architect | YES |
| After architecture | Before preview/planner | YES |
| After preview | Before planner (UI projects) | YES (skip for non-UI) |
| After project plan | Before developer | Guided mode only |
| After each epic | During development | Guided mode only |
| After code review (if issues) | Before re-spawning developer | Only if BLOCKERs |
| After QA | Before devops/security | YES |
| After security audit (if run) | Before devops/docs | Only if CRITICAL findings |
| Branch disposition | After everything | YES |
| Final summary | After everything | YES |

### Autonomy Levels

| Level | When | Checkpoints |
|-------|------|------------|
| **Guided** (default) | User seems new or project is complex | Every phase |
| **Semi-autonomous** | "Just check with me on the big stuff" | Requirements, architecture, preview, QA, final |
| **Autonomous** | "Just build it" / "don't bother me" | Requirements (mandatory), final only |

Detect from user's language. Detailed instructions = Guided. "Handle it" = Autonomous.

**⛔ AUTONOMY DOES NOT OVERRIDE MANDATORY STEPS:**
Even in Autonomous mode, these steps ALWAYS require user interaction — they cannot be auto-completed or skipped:
1. **The Grill (req-engineer Step 3.5)** — adversarial stress-test questions. User must answer.
2. **Prototype Walkthrough Choice (req-engineer Step 6.5)** — user must choose visual or text-based.
3. **Requirements checkpoint** — user must approve requirements.md.

"Just build it" means fewer checkpoints during development, NOT skipping requirements validation.

**⛔ CONTINUOUS EXECUTION IN AUTONOMOUS/SEMI-AUTONOMOUS MODE:**
Between non-checkpoint phases, execute continuously. Do NOT:
- Ask "Ready to proceed?" between phases that don't require checkpoints
- Wait for confirmation before spawning the next agent
- Summarize what just happened and ask if you should continue

Instead: spawn the next agent immediately, update the ledger, provide a one-line status, and keep going. The user opted into autonomy — respect that by not interrupting them.

---

## Error Recovery

| Situation | Action |
|-----------|--------|
| Agent fails | Retry once. If still fails, tell user. |
| User rejects checkpoint | Append feedback, re-spawn ONLY that agent. |
| Requirements change mid-pipeline | Re-run from affected agent forward. Update ledger with "Requirements changed" entry. |
| User wants to skip a step | Warn consequences. Allow if they insist — **EXCEPT The Grill and Prototype Walkthrough Choice, which are NEVER skippable.** |
| QA finds >10 bugs | Suggest re-reviewing architecture first. |
| Fix-review-QA loop >3 iterations | Stop. Suggest architect reassessment. Log in ledger as "Fix loop exceeded — escalated." |
| Conversation interrupted | On resume, read `.sdlc/progress.md` to recover state. Never rely on memory alone. |
| Ledger file missing on resume | Fall back to file detection. Warn user that progress tracking was lost. Recreate ledger from detected state. |

---

## Status Updates

Between agents, keep the user informed:

```
--------------------------------------
completed: Requirements (requirements.md)
running:   Architecture agent...
--------------------------------------
```

After full pipeline:

```
======================================
PROJECT COMPLETE

Files generated:
  - requirements.md    — X functional, Y non-functional requirements
  - plan.md            — Architecture with security
  - task-graph.md    — X epics, Y tasks across Z waves
  - .sdlc/preview/     — Visual preview (approved)
  - src/               — X files
  - tests/             — X tests, all passing (verified by running)
  - review-report.md   — APPROVED (verified by running linters + security scanners)
  - bug-report.md      — APPROVED (0 bugs found via real tool testing)
  - security-report.md — [APPROVED / N/A per profile]
  - DEPLOYMENT.md      — CI/CD + Docker + monitoring (tested, health checks pass)
  - docs/              — Full documentation suite (examples tested against running API)
  - .sdlc/progress.md  — Full build ledger (all phases tracked)

Next steps:
  1. Review prototypes one more time
  2. Deploy to staging
  3. Run smoke tests (we'll provide test script)
  4. Deploy to production
======================================
```

Then immediately present **Branch Disposition** options (see above).

---

## The Tool Execution Philosophy

This orchestrator enforces one principle: **Everything is proved with tools, nothing is assumed.**

| Bad Approach | Good Approach | This Orchestrator |
|---|---|---|
| "I read the code, it looks correct" | Run the tests, verify they pass | Agent runs tests, shows output |
| "The API should work" | Curl the endpoint, check response | Agent curl's every endpoint, logs output |
| "The database saves data" | Query it directly, verify rows exist | Agent queries database, shows results |
| "Docker image builds fine" | Build it, run it, verify it starts | Agent builds, runs, checks health check |
| "The docs are accurate" | Run the Quick Start on a fresh machine | Agent runs it, logs every step |
| "The code is secure" | Run security scanners, fix findings | Agent runs Bandit/Semgrep, reports CVEs |
| "Tests cover the code" | Measure coverage, identify gaps | Agent measures coverage, writes additional tests |
| "No secrets are leaked" | Scan git history for exposed credentials | Agent runs git log -p -S, reports findings |

**The result**: You have a production-ready product where every claim is backed by real tool output. No surprises. No "I assumed it would work."

---

## When to Use This Skill

Use `/idk` whenever you have a software development task:

- **"Build me a task manager"** → runs full pipeline
- **"Add login to my app"** → runs architect→preview→planner→developer→reviewer→QA
- **"Deploy to AWS"** → runs devops-engineer
- **"Test everything"** → runs qa-engineer
- **"Fix this bug"** → runs QA (diagnose) → developer → reviewer → QA (retest)
- **"Review my code"** → runs code-reviewer
- **"Write the API docs"** → runs tech-writer
- **"Security audit this app"** → runs security-auditor
- **"What should I build next?"** → suggests next tasks from task-graph.md

Or just describe what you want and let the orchestrator figure out which pipeline to run.
