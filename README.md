# SDLC Pipeline — Claude Code Skills

A complete Software Development Lifecycle pipeline built as Claude Code skills. One command builds an entire project — from requirements gathering to deployment-ready code with documentation.

## How It Works

You talk to one skill — **`idk`** — and it orchestrates 8 specialized agents automatically:

```
You → idk → req-engineer → sw-architect → proj-manager → sw-developer → code-reviewer → qa-engineer → devops-engineer → tech-writer
```

Just say what you want in plain English:

```
"I want to build a task management app with teams, deadlines, and notifications"
```

The pipeline interviews you, designs the architecture, breaks it into tasks, writes the code, reviews it, tests it, sets up deployment, and writes documentation — all automatically.

## Commands

| What you say | What happens |
|-------------|-------------|
| "Build me a new app" | Full pipeline: requirements → code → deploy → docs |
| "Add a payment feature" | New feature on existing code |
| "Remove the chat feature" | Safe removal with impact analysis |
| "Refactor the auth module" | Analyze + improve existing code |
| "Login is broken" | Diagnose → fix → review → retest |
| "Ship it to production" | DevOps: CI/CD, Docker, monitoring |
| "Check this code" | Code review against the plan |
| "Is this ready?" | Full QA testing |
| "Write the docs" | Full documentation suite |
| "Plan this out" | Requirements → architecture → tasks (no code) |
| "Continue" | Detects progress, resumes where it stopped |

## The Skills

| # | Skill | What It Does | Output |
|---|-------|-------------|--------|
| 0 | **idk** | Orchestrator — single entry point, dispatches all other skills | Delegates to skills below |
| 1 | **req-engineer** | Interviews you, gathers requirements, creates wireframes/prototypes | `requirements.md` |
| 2 | **sw-architect** | Designs architecture, tech stack, security, infrastructure | `plan.md` |
| 3 | **proj-manager** | Breaks plan into epics, stories, tasks with acceptance criteria | `project-plan.md` |
| 4 | **sw-developer** | Implements code with OOP, comments, modular design, unit tests | Working code + tests |
| 5 | **code-reviewer** | Reviews code against plan for quality, security, performance | `review-report.md` |
| 6 | **qa-engineer** | Tests everything — functional, edge cases, security, performance | `bug-report.md` |
| 7 | **devops-engineer** | Sets up CI/CD, Docker, monitoring, backups, environments | `DEPLOYMENT.md` |
| 8 | **tech-writer** | Generates full documentation suite | `docs/` directory |

## What You Get

After a full pipeline run, your project contains:

```
my-project/
├── requirements.md          # Requirements with wireframes/prototypes
├── plan.md                  # Architecture, tech stack, security, ADRs
├── project-plan.md          # Epics, stories, tasks, acceptance criteria
├── src/                     # Production code with comments on every line
├── tests/                   # Unit + integration tests
├── review-report.md         # Code review results
├── bug-report.md            # QA results
├── DEPLOYMENT.md            # Deployment instructions
├── Dockerfile               # Production-grade container
├── docker-compose.yml       # Local dev environment
├── .github/workflows/       # CI/CD pipeline
├── docs/
│   ├── api.md               # API documentation
│   ├── developer-guide.md   # Developer onboarding
│   ├── deployment-guide.md  # Deployment procedures
│   ├── user-guide.md        # End-user guide
│   └── changelog.md         # Version history
└── README.md                # Project README
```

## Installation

### 1. Clone this repo

```bash
git clone https://github.com/ub1979/sw_eng.git
```

### 2. Register skills in Claude Code

Add this to your project's `CLAUDE.md` or `~/.claude/CLAUDE.md`:

```markdown
## Skills

- /path/to/sw_eng/idk/SKILL.md
- /path/to/sw_eng/req-engineer/SKILL.md
- /path/to/sw_eng/sw-architect/SKILL.md
- /path/to/sw_eng/proj-manager/SKILL.md
- /path/to/sw_eng/sw-developer/SKILL.md
- /path/to/sw_eng/code-reviewer/SKILL.md
- /path/to/sw_eng/qa-engineer/SKILL.md
- /path/to/sw_eng/devops-engineer/SKILL.md
- /path/to/sw_eng/tech-writer/SKILL.md
```

### 3. Start using it

```
You: I want to build an invoice management system with PDF export
```

That's it. The `idk` skill triggers automatically and runs the pipeline.

## Pipeline Flows

| Scenario | Flow |
|----------|------|
| New project from scratch | req → architect → planner → developer → reviewer → QA → devops → docs |
| New feature on existing code | req → architect (hybrid) → planner → developer → reviewer → QA |
| Remove a feature | architect (impact analysis) → planner → developer → reviewer → QA |
| Improve existing code | architect (analysis) → planner → developer → reviewer → QA |
| Fix a bug | QA (diagnose) → developer (fix) → reviewer → QA (retest) |
| Deploy existing code | devops only |
| Document existing code | tech-writer only |
| Plan only, no code | req → architect → planner |

## Checkpoints

The orchestrator stops at key moments for your approval:

1. **After requirements** — review wireframes before architecture begins
2. **After architecture** — approve tech stack and security plan
3. **After QA** — confirm all bugs are fixed before deployment
4. **Final summary** — overview of everything that was built

You can control how often it checks in:
- **Guided** (default) — asks at every phase
- **Semi-autonomous** — "just check with me on the big stuff"
- **Autonomous** — "just build it" (still asks about requirements)

## Requirements

- [Claude Code](https://claude.ai/claude-code) (Anthropic's CLI tool)
- These skills are Claude Code specific — they won't work with other AI tools

## License

MIT
