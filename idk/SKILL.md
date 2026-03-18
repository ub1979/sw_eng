---
name: idk
description: The single entry point that orchestrates the entire software development lifecycle. Dispatches 8 specialized agents (req-engineer, sw-architect, proj-manager, sw-developer, code-reviewer, qa-engineer, devops-engineer, tech-writer) in the right order based on what you ask for. Use this skill whenever the user mentions build me, create, new project, new app, modify, add feature, remove feature, fix bug, deploy, test, review code, write docs, I want to build, make me a, develop, start a project, continue working, what's next, ship it, refactor, improve, debug, go live, CI/CD, document this, plan this, architect this, or ANY software development request. This is the default entry point for all software development work.
---

# IDK — Software Development Lifecycle Orchestrator

The single entry point for all software development work. You talk to this skill — it spawns the right agents in the right order, passes outputs between them, and only interrupts you at critical decision points.

**Architecture**: This is a **SKILL** (lives in the main conversation for user interaction) that dispatches **AGENTS** (autonomous sub-processes) for the heavy lifting.

---

## Step 0 — Detect Intent

When the user gives input, determine:

1. **Command** — which command matches (explicit or natural language)
2. **Path** — is there an existing codebase?
3. **Documents** — do requirements.md, plan.md, project-plan.md already exist?
4. **Progress** — how far along is the project?

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

Follow the `req-engineer` skill instructions in the main conversation:
- Conduct interview (2-3 rounds)
- Generate `requirements.md` with prototypes
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
2. Requirements interview for new feature (orchestrator handles)
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

1. Requirements interview (orchestrator)
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
| **Retry once on failure** | If fails again, tell user and suggest manual intervention |
| **Pass user feedback** | Re-spawn ONLY the rejected agent with feedback appended |

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

---

## Error Recovery

| Situation | Action |
|-----------|--------|
| Agent fails | Retry once. If still fails, tell user. |
| User rejects checkpoint | Append feedback, re-spawn ONLY that agent. |
| Requirements change mid-pipeline | Re-run from affected agent forward. |
| User wants to skip a step | Warn consequences. Allow if they insist. |
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
  - tests/             — X tests, all passing
  - review-report.md   — APPROVED
  - bug-report.md      — APPROVED (0 bugs)
  - DEPLOYMENT.md      — CI/CD + Docker + monitoring
  - docs/              — Full documentation suite

Next steps:
  1. Review prototypes one more time
  2. Deploy to staging
  3. Smoke test
  4. Deploy to production
======================================
```
