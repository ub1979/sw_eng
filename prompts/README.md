# Skill Prompts — Software Development Pipeline

These prompts are used to create skills that form a complete software development pipeline. Each prompt generates one skill.

## The Orchestrator

**You only need one skill to remember: `sdlc-orchestrator`.** It automatically invokes the right skills in the right order based on what you ask for.

```
User → sdlc-orchestrator → delegates to the right skills automatically
```

### Commands

| Command | What you say | What happens |
|---------|-------------|--------------|
| `new` | "build me a new app" | Full pipeline: requirements → architecture → planning → coding → review → QA → deploy → docs |
| `add` | "add payment feature" | req-engineer → architect (hybrid) → plan → code → review → QA |
| `del` | "remove the chat feature" | Impact analysis → removal tasks → code → review → regression test |
| `modify` | "refactor the auth module" | Codebase analysis → improvement plan → code → review → QA |
| `fix` | "login is broken" | QA diagnose → developer fix → review → retest |
| `deploy` | "ship it to production" | DevOps setup: CI/CD, Docker, monitoring |
| `review` | "check this code" | Code review against architecture plan |
| `test` | "is this ready?" | Full QA testing |
| `docs` | "write the docs" | Full documentation suite |
| `plan` | "plan this out" | Requirements → architecture → task breakdown (no code) |
| `resume` | "continue" | Detect progress, resume from where it stopped |

---

## The Pipeline (under the hood)

```
req-engineer → sw-architect → proj-manager → sw-developer → code-reviewer → qa-engineer → devops-engineer → tech-writer
                                                                ↑               |
                                                                └── fix loop ───┘
```

## All Prompts

| # | File | Skill | Input | Output |
|---|------|-------|-------|--------|
| 0 | [sdlc-orchestrator.md](sdlc-orchestrator.md) | **Orchestrator** | User intent | Delegates to skills below |
| 1 | [req-engineer.md](req-engineer.md) | Requirements Engineer | User interview | `requirements.md` with prototypes |
| 2 | [sw-architect.md](sw-architect.md) | Software Architect | `requirements.md` or codebase | `plan.md` with security architecture |
| 3 | [proj-manager.md](proj-manager.md) | Project Manager | `plan.md` + `requirements.md` | `project-plan.md` with design system |
| 4 | [sw-developer.md](sw-developer.md) | Software Developer | `project-plan.md` | Working code + unit tests |
| 5 | [code-reviewer.md](code-reviewer.md) | Code Reviewer | Code + `plan.md` | `review-report.md` |
| 6 | [qa-engineer.md](qa-engineer.md) | QA Engineer | Code + `project-plan.md` | `bug-report.md` |
| 7 | [devops-engineer.md](devops-engineer.md) | DevOps Engineer | Code + `plan.md` | CI/CD, Docker, monitoring, `DEPLOYMENT.md` |
| 8 | [tech-writer.md](tech-writer.md) | Technical Writer | Code + all docs | `docs/` directory |

## Flow for Different Scenarios

| Scenario | Flow |
|----------|------|
| New project from scratch | 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 |
| Have requirements doc already | 2 → 3 → 4 → 5 → 6 → 7 → 8 |
| New features on existing code | 1 → 2 (hybrid) → 3 → 4 → 5 → 6 → 7 → 8 |
| Remove a feature | 2 (impact analysis) → 3 → 4 → 5 → 6 |
| Improve existing code only | 2 (codebase analysis) → 3 → 4 → 5 → 6 → 7 |
| Fix a bug | 6 (diagnose) → 4 (fix) → 5 (review) → 6 (retest) |
| Already have plan.md | 3 → 4 → 5 → 6 → 7 → 8 |
| Code exists, need deployment | 7 |
| Code exists, need docs | 8 |
| Just want a plan, no code | 1 → 2 → 3 |
