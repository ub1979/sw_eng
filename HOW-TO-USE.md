# How to Use the SDLC Pipeline

You only need to remember one skill: **`idk`**

It's the single entry point that handles everything. Just tell it what you want in plain English — it figures out the rest.

---

## Setup

Make sure all skill folders are registered in your Claude Code configuration so they can be discovered. Each skill lives in its own folder under `/skills/`:

```
skills/
├── idk/               # The orchestrator (start here)
├── req-engineer/      # Requirements gathering
├── sw-architect/      # Architecture design
├── proj-manager/      # Task breakdown & planning
├── sw-developer/      # Code implementation
├── code-reviewer/     # Code quality review
├── qa-engineer/       # Testing & bug reports
├── devops-engineer/   # CI/CD, Docker, monitoring
└── tech-writer/       # Documentation
```

---

## Quick Start

Just talk to Claude. The `idk` skill triggers automatically. Here are real examples:

### Build Something New

```
You: I want to build a task management app with teams, deadlines, and notifications
```

What happens behind the scenes:
1. `idk` detects this is a `new` project
2. It interviews you about requirements (2-3 rounds of questions)
3. Generates `requirements.md` with wireframes — asks you to review
4. Spawns architect agent → `plan.md`  — asks you to review
5. Spawns planner agent → `project-plan.md` with all tasks
6. Spawns developer agent → writes all the code + tests
7. Spawns reviewer agent → checks code quality
8. Spawns QA agent → finds bugs, developer fixes them
9. Spawns devops + docs agents in parallel → deployment + documentation

You get a complete, tested, documented, deployable project.

### Add a Feature to Existing Code

```
You: Add a Stripe payment system to my app at ./myproject
```

What happens:
1. `idk` detects `add` command + existing codebase
2. Interviews you about the payment feature
3. Architect analyzes your existing code + designs how payments fit in
4. Planner creates tasks for the new feature
5. Developer implements it matching your existing code style
6. Reviewer + QA verify everything works

### Fix a Bug

```
You: The login page crashes when I enter a long email address
```

What happens:
1. `idk` detects `fix` command
2. QA agent diagnoses the bug
3. Developer agent fixes it + adds a regression test
4. Reviewer checks the fix
5. QA retests to confirm it's resolved

### Deploy Your App

```
You: Deploy this to production
```

What happens:
1. `idk` spawns the devops agent
2. Creates Dockerfile, docker-compose, CI/CD pipeline, monitoring, alerts
3. Writes `DEPLOYMENT.md` with full instructions

### Just Plan, No Code

```
You: Plan out an e-commerce platform but don't write any code yet
```

What happens:
1. Requirements interview → `requirements.md`
2. Architecture design → `plan.md`
3. Task breakdown → `project-plan.md`
4. Stops. No code written.

---

## All Commands

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

---

## What Gets Generated

After a full `new` pipeline, your project folder looks like this:

```
my-project/
├── requirements.md      # What to build, with wireframes/prototypes
├── plan.md              # Architecture, tech stack, security, ADRs
├── project-plan.md      # Epics, stories, tasks, acceptance criteria
├── src/                 # Production code with comments
├── tests/               # Unit + integration tests
├── review-report.md     # Code review results
├── bug-report.md        # QA results
├── DEPLOYMENT.md        # How to deploy
├── docs/
│   ├── api.md           # API documentation
│   ├── developer-guide.md
│   ├── deployment-guide.md
│   ├── user-guide.md
│   └── changelog.md
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/   # CI/CD pipeline
└── README.md
```

---

## Checkpoints (Where It Asks You)

The orchestrator doesn't just run blindly. It stops at key moments:

1. **After requirements** — "Review the wireframes. This is the cheapest time to change anything."
2. **After architecture** — "Here's the tech stack and security plan. Approve?"
3. **After QA** — "QA found 3 bugs and fixed them. Ready to deploy?"
4. **Final summary** — Shows everything that was built

You can control how often it checks in:
- **Guided** (default) — asks at every phase
- **Semi-autonomous** — "just check with me on the big stuff"
- **Autonomous** — "just build it, don't bother me" (still asks about requirements)

---

## Using Individual Skills Directly

You don't have to use `idk`. You can call any skill directly:

```
You: Use the sw-architect skill to review my codebase at ./myapp
```

```
You: Run the qa-engineer on this project
```

```
You: I need the tech-writer to document my API
```

This is useful when you want to run just one phase without the full pipeline.

---

## Tips

- **Be specific about what you want** — "build a REST API for managing invoices with PDF generation" beats "build something"
- **Point to existing code** — mention the path so it matches your patterns
- **Review the requirements carefully** — changes are cheap at this stage, expensive later
- **Let it fix its own bugs** — the fix-review-QA loop runs automatically until everything passes
- **Resume anytime** — if you close the conversation, just say "continue" and it picks up where it left off
