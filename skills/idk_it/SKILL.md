---
name: idk_it
description: The single entry point that orchestrates the entire software development lifecycle. Dispatches 8 specialized agents (req-engineer, sw-architect, proj-manager, sw-developer, code-reviewer, qa-engineer, devops-engineer, tech-writer) in the right order based on what you ask for. Use this skill whenever the user mentions build me, create, new project, new app, modify, add feature, remove feature, fix bug, deploy, test, review code, write docs, I want to build, make me a, develop, start a project, continue working, what's next, ship it, refactor, improve, debug, go live, CI/CD, document this, plan this, architect this, or ANY software development request. This is the default entry point for all software development work.
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

### Why This Matters

Each agent has a 50-100+ line skill document defining a rigorous multi-step methodology with specific tool executions, output formats, and quality gates. When the orchestrator "does it quickly" instead of spawning the agent, it skips 90% of that methodology. The user built these skills specifically to get that rigor. Bypassing them defeats the entire purpose.

---

The single entry point for all software development work. You talk to this skill — it spawns the right agents in the right order, passes outputs between them, and only interrupts you at critical decision points.

**Architecture**: This is a **SKILL** (lives in the main conversation for user interaction) that dispatches **AGENTS** (autonomous sub-processes) for the heavy lifting.

**Core Promise**: Every agent uses REAL TOOLS to build, test, review, and deploy. No "I read the code and it looks correct." Every claim is backed by tool execution with proof.

---

## Tool & Dependency Management

Before agents start working, this orchestrator ensures they have everything they need:

### Auto-Install Language Runtimes
```bash
# Node.js (for web apps, APIs, CLI tools)
which node || (curl -sL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs)

# Python (for FastAPI, scripts, data work)
which python3 || apt-get install -y python3 python3-pip python3-venv

# Go (for high-performance CLI tools)
which go || (wget https://go.dev/dl/go1.21.linux-amd64.tar.gz && tar -C /usr/local -xzf go*.tar.gz)

# Docker (for containerization, deployment)
which docker || (curl -fsSL https://get.docker.com | sh && usermod -aG docker $USER)

# Git (for version control)
which git || apt-get install -y git

# PostgreSQL/MySQL client (for database testing)
which psql || apt-get install -y postgresql-client
which mysql || apt-get install -y mysql-client
```

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
3. **Documents** — do requirements.md, plan.md, project-plan.md already exist?
4. **Progress** — how far along is the project?
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
| `new` | "new project", "build from scratch", "start fresh", "create new", "I want to build" | req -> architect -> planner -> developer -> reviewer -> QA -> devops+docs |
| `modify` | "modify", "change", "refactor", "improve", "restructure" | architect (analysis) -> planner -> developer -> reviewer -> QA |
| `add` | "add feature", "extend", "I also need", "build on top of" | req -> architect (hybrid) -> planner -> developer -> reviewer -> QA |
| `del` | "remove feature", "delete", "rip out", "get rid of" | architect (impact) -> planner -> developer -> reviewer -> QA (regression) |
| `fix` | "fix bug", "broken", "not working", "error", "debug" | QA (diagnose) -> developer -> reviewer -> QA (retest) |
| `deploy` | "deploy", "ship it", "go live", "push to production", "set up CI/CD" | devops-engineer only |
| `review` | "review this code", "check quality", "audit" | code-reviewer -> (optional developer fix loop) |
| `test` | "test this", "run QA", "find bugs", "verify", "is this ready" | qa-engineer -> (optional developer fix loop) |
| `docs` | "write docs", "document this", "README", "API docs" | tech-writer only |
| `plan` | "plan this", "design architecture", "architect this" | req -> architect -> planner (no code) |
| `resume` | "continue", "next task", "keep going", "what's next" | detect progress, resume from where it stopped |

### Auto-Detection Logic

```
IF no code + no docs -> probably "new"
IF code exists + user mentions changes -> probably "modify" or "add"
IF code exists + user mentions removal -> probably "del"
IF code exists + user mentions problems -> probably "fix"
IF code exists + user mentions deploy -> "deploy"
IF code exists + user mentions docs -> "docs"
IF ambiguous -> ask ONE question: "What would you like to do?" with options
```

### State Detection

Check working directory for existing files:

| File | Means |
|------|-------|
| `requirements.md` | Requirements phase complete |
| `plan.md` | Architecture phase complete |
| `project-plan.md` | Planning phase complete |
| `src/` or code files | Development in progress/complete |
| `review-report.md` | Code review done |
| `bug-report.md` | QA done or in progress |
| `DEPLOYMENT.md` | DevOps setup done |
| `docs/` directory | Documentation done |

If documents exist, don't redo completed phases. Ask: "I see [X, Y, Z] already done. Continue from [next step]?"

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

Keep this to 5-8 lines. For simple commands (deploy, docs), skip confirmation and start.

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

**Phase 2: Architecture — spawn agent**

Spawn `sw-architect` agent with:
- Input: requirements.md path
- Task: greenfield mode, generate plan.md with full security architecture
- Wait for completion, read plan.md

MANDATORY CHECKPOINT: "Architecture plan ready. Key decisions: [2-3 bullets]. Review plan.md. Say 'approved' to continue."

If user requests changes, re-spawn architect with feedback appended.

**Phase 3: Project Planning — spawn agent**

Spawn `proj-manager` agent with:
- Input: plan.md + requirements.md paths
- Task: full breakdown with design system if UI project
- Wait for completion, read project-plan.md

CHECKPOINT: "Project broken into X epics, Y stories, Z tasks. Estimated: X sprints. Review project-plan.md."

**Phase 4: Development — spawn agent**

Spawn `sw-developer` agent with:
- Input: project-plan.md + plan.md + requirements.md paths
- Task: implement all tasks in dependency order, scaffolding first

After each epic, provide status: "Epic E-XXX complete. X tasks done, Y remaining."

**Phase 5: Code Review — spawn agent**

Spawn `code-reviewer` agent with:
- Input: codebase + plan.md + project-plan.md
- Task: full review, write review-report.md

If CHANGES REQUIRED:
1. Spawn sw-developer: fix issues from review-report.md
2. Spawn code-reviewer: re-review changed files
3. Repeat until APPROVED

**Phase 6: QA Testing — spawn agent**

Spawn `qa-engineer` agent with:
- Input: codebase + project-plan.md + requirements.md
- Task: all 6 testing levels, write bug-report.md

If bugs found:
1. Spawn sw-developer: fix bugs from bug-report.md
2. Spawn code-reviewer: review fixes
3. Spawn qa-engineer: retest + regression
4. Repeat until APPROVED

MANDATORY CHECKPOINT: "QA complete. Verdict: [APPROVED/X bugs remaining]. Ready for deployment?"

**Phase 7 & 8: DevOps + Docs — spawn in PARALLEL**

Spawn both simultaneously (they're independent):
- `devops-engineer`: CI/CD, Docker, monitoring -> DEPLOYMENT.md
- `tech-writer`: full docs suite -> README.md + docs/

Wait for both to complete.

**DONE — Final Summary**

### Command: `add` (New Feature)

1. Scan existing codebase (orchestrator reads directly)
2. Requirements interview for new feature (orchestrator handles) — **MUST include The Grill (Step 3.5) and Prototype Walkthrough Choice (Step 6.5) from req-engineer. No exceptions.**
3. Spawn sw-architect (hybrid mode — impact analysis)
4. Spawn proj-manager (tasks for new feature)
5. Spawn sw-developer -> code-reviewer -> qa-engineer (fix loops as needed)

### Command: `del` (Remove Feature)

1. Scan codebase for feature's files, routes, models, tests
2. Spawn sw-architect (removal impact analysis)
3. CHECKPOINT: "Removing [feature] affects [X] files. [Things that break]. Proceed?"
4. Spawn proj-manager (removal tasks)
5. Spawn sw-developer -> code-reviewer -> qa-engineer (regression test)
6. Spawn tech-writer (update docs)

### Command: `modify` (Refactor/Improve)

1. Spawn sw-architect (codebase analysis mode)
2. CHECKPOINT: "Found [X] issues. Top 3: [list]. Which to implement?"
3. Spawn proj-manager (tasks for approved improvements)
4. Spawn sw-developer -> code-reviewer -> qa-engineer

### Command: `fix` (Bug Fix)

1. Ask user: "What's happening? Expected? Error messages?" OR read existing bug-report.md
2. Spawn qa-engineer (diagnose mode) -> bug-report.md
3. Spawn sw-developer (fix bugs + regression tests)
4. Spawn code-reviewer (review fix)
5. Spawn qa-engineer (retest + regression)
6. Loop steps 3-5 until APPROVED

### Command: `deploy`

Spawn devops-engineer agent. Done.

### Command: `review`

Spawn code-reviewer agent. If issues found, offer to fix.

### Command: `test`

Spawn qa-engineer agent. If bugs found, offer to fix.

### Command: `docs`

Spawn tech-writer agent. Done.

### Command: `plan`

1. Requirements interview (orchestrator) — **MUST include The Grill (Step 3.5) and Prototype Walkthrough Choice (Step 6.5) from req-engineer. No exceptions.**
2. Spawn sw-architect -> plan.md
3. Spawn proj-manager -> project-plan.md
4. Stop — no code.

### Command: `resume`

1. Check working directory for existing files
2. Determine where pipeline stopped
3. Ask: "I see [X, Y] done. Continue from [next step]?"
4. Resume by spawning the next agent

---

## Agent Spawning Rules

| Rule | Details |
|------|---------|
| **Always pass full context** | Every agent gets paths to ALL relevant docs + working directory |
| **One at a time** (default) | Sequential — wait for each to finish |
| **Parallel when independent** | DevOps + tech-writer at the end only |
| **Read output before next** | Read output file for checkpoint info and next agent context |
| **Retry once on failure** | If fails again, escalate with clear error and recovery steps |
| **Pass user feedback** | Re-spawn ONLY the rejected agent with feedback appended |

---

## Agent Tool Execution Requirements

**CRITICAL**: Every agent MUST execute with REAL TOOLS and report evidence. No agent may claim success by "reading code" or "assuming it works."

### What Each Agent Must Execute

| Agent | Must Execute | Proves |
|-------|--------------|--------|
| **req-engineer** | WebSearch to validate competitive features; build UI prototypes in HTML/CSS; run examples to verify API specs | Requirements are real, feasible, not just wishful |
| **sw-architect** | Compile/run existing codebase; run SAST tools (Bandit, Semgrep); run dependency scanners (npm audit, pip-audit); build POC for risky decisions | Architecture decisions are sound, not guesses |
| **proj-manager** | Validate design system choices with actual component libraries; test responsive breakpoints with browser tools; verify accessibility with WCAG validators | Plan is realistic, not speculative |
| **sw-developer** | Run dev server; execute unit tests; run linter; build Docker image; verify code compiles; start the application | Code actually works, not just syntactically correct |
| **code-reviewer** | Run tests; run linters; run SAST tools (Bandit, Semgrep, ESLint-security); build Docker image; scan dependencies for CVEs | Code review backed by tool evidence, not opinion |
| **qa-engineer** | Run Playwright for UI; run curl/httpx for APIs; query database directly for data verification; run unit test suite; produce bug report with tool output | Bugs are REAL (with reproduction steps + proof) not speculative |
| **devops-engineer** | Build Docker image; test CI/CD pipeline; verify health checks pass; test rollback procedures; run load tests; execute backup/restore drills | Deployment is tested, not hoped-for |
| **tech-writer** | Test API examples against running endpoints; run Quick Start guide on fresh machine; execute CLI commands; verify links work; compile code examples | Documentation is accurate, tested, not outdated |

### Agent Context Provided by Orchestrator

When spawning any agent, this orchestrator provides:

1. **Working directory** — where code is, where to write output
2. **Required tools pre-installed** — Node.js, Python, Docker, Git, Playwright, pytest, curl, etc.
3. **Input documents** — requirements.md, plan.md, project-plan.md, existing code
4. **Error recovery support** — if a tool fails, this orchestrator:
   - Catches the error
   - Analyzes what failed
   - Installs/fixes the tool if possible
   - Retries the command
   - Escalates to user if unrecoverable
5. **Evidence collection** — all tool output (logs, test results, screenshots) is saved for reporting

### Example: Developer Agent Workflow

When developer agent spawns, it:
```bash
# 1. Read project-plan.md to understand what to build
cat project-plan.md

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
- project-plan.md: [path] (if exists)
- Existing code: [path] (if exists)

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
```

---

## Checkpoint Rules

| Checkpoint | When | Mandatory? |
|-----------|------|-----------|
| After requirements | Before architect | YES |
| After architecture | Before planner | YES |
| After project plan | Before developer | Guided mode only |
| After each epic | During development | Guided mode only |
| After code review (if issues) | Before re-spawning developer | Only if BLOCKERs |
| After QA | Before devops | YES |
| Final summary | After everything | YES |

### Autonomy Levels

| Level | When | Checkpoints |
|-------|------|------------|
| **Guided** (default) | User seems new or project is complex | Every phase |
| **Semi-autonomous** | "Just check with me on the big stuff" | Requirements, architecture, QA, final |
| **Autonomous** | "Just build it" / "don't bother me" | Requirements (mandatory), final only |

Detect from user's language. Detailed instructions = Guided. "Handle it" = Autonomous.

**⛔ AUTONOMY DOES NOT OVERRIDE MANDATORY STEPS:**
Even in Autonomous mode, these steps ALWAYS require user interaction — they cannot be auto-completed or skipped:
1. **The Grill (req-engineer Step 3.5)** — adversarial stress-test questions. User must answer.
2. **Prototype Walkthrough Choice (req-engineer Step 6.5)** — user must choose visual or text-based.
3. **Requirements checkpoint** — user must approve requirements.md.

"Just build it" means fewer checkpoints during development, NOT skipping requirements validation.

---

## Error Recovery

| Situation | Action |
|-----------|--------|
| Agent fails | Retry once. If still fails, tell user. |
| User rejects checkpoint | Append feedback, re-spawn ONLY that agent. |
| Requirements change mid-pipeline | Re-run from affected agent forward. |
| User wants to skip a step | Warn consequences. Allow if they insist — **EXCEPT The Grill and Prototype Walkthrough Choice, which are NEVER skippable.** |
| QA finds >10 bugs | Suggest re-reviewing architecture first. |
| Fix-review-QA loop >3 iterations | Stop. Suggest architect reassessment. |

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
  - project-plan.md    — X epics, Y stories, Z tasks
  - src/               — X files
  - tests/             — X tests, all passing (verified by running)
  - review-report.md   — APPROVED (verified by running linters + security scanners)
  - bug-report.md      — APPROVED (0 bugs found via real tool testing)
  - DEPLOYMENT.md      — CI/CD + Docker + monitoring (tested, health checks pass)
  - docs/              — Full documentation suite (examples tested against running API)

Next steps:
  1. Review prototypes one more time
  2. Deploy to staging
  3. Run smoke tests (we'll provide test script)
  4. Deploy to production
======================================
```

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

**The result**: You have a production-ready product where every claim is backed by real tool output. No surprises. No "I assumed it would work."

---

## When to Use This Skill

Use `/idk` whenever you have a software development task:

- **"Build me a task manager"** → runs full pipeline
- **"Add login to my app"** → runs architect→planner→developer→reviewer→QA
- **"Deploy to AWS"** → runs devops-engineer
- **"Test everything"** → runs qa-engineer
- **"Fix this bug"** → runs QA (diagnose) → developer → reviewer → QA (retest)
- **"Review my code"** → runs code-reviewer
- **"Write the API docs"** → runs tech-writer
- **"What should I build next?"** → suggests next stories from project-plan.md

Or just describe what you want and let the orchestrator figure out which pipeline to run.
