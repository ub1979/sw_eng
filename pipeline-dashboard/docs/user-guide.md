# User Guide

## What Is This?

The **SDLC Pipeline Dashboard** turns your ideas into working software. Just describe what you want — "a portfolio website for my photography business" — and our AI agents handle everything: requirements, architecture, planning, coding, review, testing, deployment setup, and documentation.

## Quick Start

### 1. Start the App

```bash
cd pipeline-dashboard
make run
```

Open your browser to `http://localhost:8000`.

### 2. Pick Your AI

Choose from three AI providers:

| Provider | Best For | Setup |
|----------|----------|-------|
| **Ollama** | Free, private, runs locally | Install [Ollama](https://ollama.com), run `ollama serve` |
| **Claude** | High-quality code, reasoning | Install [Claude Code CLI](https://code.claude.com) |
| **Gemini** | Fast, good for simple projects | Install `gemini` or `agy` CLI |

The dashboard auto-detects which providers are available.

### 3. Describe Your Project

Type what you want in plain English:

> "I want a task management app with teams, deadlines, and email notifications. Users should be able to assign tasks, set priorities, and get reminded before deadlines."

### 4. Watch It Build

Click **Start Pipeline**. You'll see:

- **Progress bar** — overall completion percentage
- **Agent cards** — 8 specialized AI agents working in sequence:
  1. **Requirements** — interviews you and writes specs
  2. **Architect** — designs tech stack and security
  3. **Planner** — breaks work into tasks
  4. **Developer** — writes all the code
  5. **Reviewer** — checks code quality
  6. **QA** — finds and fixes bugs
  7. **DevOps** — sets up Docker and CI/CD
  8. **Writer** — writes documentation

- **Live logs** — real-time stream of what each agent is doing

### 5. Approve Checkpoints

At key moments, the pipeline pauses for your approval:

- After **Requirements** — review the spec
- After **Architecture** — approve the tech stack
- After **QA** — confirm bugs are fixed

Click **Approve & Continue** or **Request Changes** with feedback.

### 6. Download Your Project

When complete, browse all generated files:

- `requirements.md` — what was built
- `plan.md` — architecture decisions
- `project-plan.md` — task breakdown
- `src/` — all source code
- `tests/` — test suite
- `review-report.md` — code review results
- `bug-report.md` — QA results
- `DEPLOYMENT.md` — how to deploy
- `docs/` — full documentation

Click **Download All as ZIP** to save everything.

## Understanding the Dashboard

### Status Bar

Top of the screen shows:
- 🟢 **Idle** — ready to start
- 🔵 **Running** — pipeline is active
- 🟡 **Paused** — waiting for your approval at a checkpoint
- 🟢 **Complete** — all done, ready to download
- 🔴 **Failed** — an error occurred, retry available

### Agent Cards

| Icon | State | Meaning |
|------|-------|---------|
| ⏳ | Pending | Not started yet |
| ▶️ | Running | Currently working |
| ✅ | Complete | Finished successfully |
| ❌ | Failed | Error occurred |
| ⏸️ | Paused | Waiting for approval |

Click any card to see details and generated artifacts.

### Live Log Panel

Shows real-time output from the current agent:
- Timestamps on the left
- Messages on the right
- Auto-scrolls to latest
- Click **Copy** to copy all logs

## History

Click the **History** button to see past pipeline runs:

- View completed projects
- Resume paused pipelines
- Delete old projects (removes files and database record)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Ollama not reachable" | Run `ollama serve` in a terminal |
| "Claude not found" | Install Claude Code CLI and ensure it's in your PATH |
| "Gemini not found" | Install `gemini` or `agy` CLI |
| Pipeline seems stuck | Check the Live Log — the agent may be waiting for a tool to install |
| Browser tab closed | Reopen `localhost:8000` — the pipeline continues in the background |
| Want to stop a pipeline | Go to History and delete the run |

## Safety

- **Guardrails** block dangerous commands automatically
- All projects are isolated in their own folders
- Your data stays local — nothing is sent to external servers except AI provider API calls
- Review the architecture plan before approving — this is the cheapest time to change anything

## Tips

- **Be specific** — "a blog with user accounts, comments, and markdown editing" beats "a website"
- **Review checkpoints carefully** — changes after approval take longer
- **Start simple** — complex projects may take 30-60 minutes to complete
- **Keep the tab open** — while closing doesn't stop the pipeline, you miss the live experience

## Getting Help

- Check `README.md` in your generated project for architecture details
- Review `DEPLOYMENT.md` for hosting instructions
- Security questions? See `docs/SECURITY.md`
