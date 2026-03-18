# Prompt: sdlc-orchestrator

> **Create a skill called `sdlc-orchestrator` — the single entry point that orchestrates the entire software development lifecycle. It is a SKILL (lives in the main conversation, interacts with the user at checkpoints) that dispatches 8 specialized AGENTS to do the actual work. The user talks to this skill — it spawns agents, collects their outputs, passes them to the next agent, and only interrupts the user at critical decision points.**
>
> **Architecture: Skill + Agents**
>
> This is a **SKILL** (not an agent) because:
> - It needs to interact with the user at checkpoints (review requirements, approve architecture, confirm deploy)
> - It needs to show real-time progress between phases
> - It needs to change course based on user feedback mid-pipeline
>
> It dispatches **AGENTS** for the heavy lifting because:
> - Each specialist does independent work in its own context
> - Agents can run in parallel where phases are independent (e.g., devops + tech-writer)
> - Agent outputs don't clutter the main conversation
> - Each agent gets the relevant skill loaded and does its job autonomously
>
> **How delegation works:**
>
> For each phase, the orchestrator uses the Agent tool to spawn a sub-agent with a prompt like:
>
> ```
> You are acting as the [role] for this project.
> Follow the [skill-name] skill instructions exactly.
>
> Context:
> - Working directory: [path]
> - [List any input files: requirements.md at X, plan.md at Y]
> - [Any user preferences or constraints gathered so far]
>
> Task: [specific instruction for this phase]
>
> Write your output to: [output file path]
> ```
>
> The orchestrator reads the agent's output file and passes it to the next agent. The user never needs to know about the agent handoffs — they just see progress updates and checkpoints.
>
> ---
>
> **Commands (auto-detected from natural language OR explicit):**
>
> | Command | Trigger phrases | What it does |
> |---------|----------------|--------------|
> | `new` | "new project", "build from scratch", "start fresh", "create new", "I want to build" | Full pipeline: all 8 agents in sequence |
> | `modify` | "modify this", "change this", "refactor", "improve", "restructure" | Analyze + improve: architect → planner → developer → reviewer → QA |
> | `add` | "add feature", "add a new", "I also need", "extend this with", "build on top of" | New feature on existing code: req → architect (hybrid) → planner → developer → reviewer → QA |
> | `del` | "remove feature", "delete", "rip out", "get rid of", "we don't need X anymore" | Remove safely: architect (impact) → planner → developer → reviewer → QA (regression) |
> | `fix` | "fix bug", "something's broken", "not working", "error", "debug" | Fix loop: QA (diagnose) → developer → reviewer → QA (retest) |
> | `deploy` | "deploy", "ship it", "go live", "push to production", "set up CI/CD" | DevOps agent only |
> | `review` | "review this code", "check quality", "audit", "is this code good" | Code reviewer agent → (optional) developer fix loop |
> | `test` | "test this", "run QA", "find bugs", "verify", "is this ready" | QA agent → (optional) developer fix loop |
> | `docs` | "write docs", "document this", "README", "API docs" | Tech writer agent only |
> | `plan` | "plan this", "design architecture", "architect this" | Plan only: req → architect → planner (no code) |
> | `resume` | "continue", "next task", "keep going", "what's next" | Detect progress, resume from where it stopped |
>
> ---
>
> **Phase 1 — Detect Intent:**
>
> When the user gives input, determine:
>
> 1. **Command** — which of the above commands matches (can be explicit or natural language)
> 2. **Path** — is there an existing codebase? (user provides path or current directory has code)
> 3. **Documents** — do `requirements.md`, `plan.md`, `project-plan.md` already exist in the working directory?
> 4. **Progress** — how far along is the project? (detect by which documents/code already exist)
>
> **Auto-detection logic:**
>
> ```
> IF no code + no docs → probably "new"
> IF code exists + user mentions changes → probably "modify" or "add"
> IF code exists + user mentions removal → probably "del"
> IF code exists + user mentions problems → probably "fix"
> IF code exists + user mentions deploy → probably "deploy"
> IF code exists + user mentions docs → probably "docs"
> IF ambiguous → ask ONE question: "What would you like to do?" and present the options
> ```
>
> **State detection — check what already exists in working directory:**
>
> | File exists | Means |
> |-------------|-------|
> | `requirements.md` | Requirements phase complete |
> | `plan.md` | Architecture phase complete |
> | `project-plan.md` | Planning phase complete |
> | `src/` or code files | Development in progress or complete |
> | `review-report.md` | Code review done |
> | `bug-report.md` | QA done (or in progress) |
> | `DEPLOYMENT.md` | DevOps setup done |
> | `docs/` directory | Documentation done |
>
> If documents already exist, **don't redo completed phases** — start from where things left off. Ask the user: "I see `requirements.md` and `plan.md` already exist. Do you want me to continue from project planning, or start over?"
>
> ---
>
> **Phase 2 — Confirm the Plan:**
>
> Before starting, briefly tell the user what's going to happen:
>
> ```
> Got it — you want to [build a new project / add a feature / etc.].
>
> Here's what I'll do:
> 1. [First agent] — [what it will do]
> 2. [Second agent] — [what it will do]
> ...
>
> I'll need your input for requirements gathering, then I'll work autonomously
> through the rest. Ready to start?
> ```
>
> **Keep this brief — 5-8 lines max.** Don't over-explain.
>
> If the command is clear and simple (like `deploy` or `docs`), skip confirmation and just start.
>
> ---
>
> **Phase 3 — Execute the Pipeline:**
>
> ### Command: `new` (Full Pipeline)
>
> **Step 1: Requirements Gathering (SPECIAL — orchestrator handles this directly)**
>
> The requirements phase is the ONE phase the orchestrator handles in the main conversation (not via agent), because it requires a multi-round interview with the user. Follow the `req-engineer` skill instructions directly:
> - Conduct the interview (2-3 rounds)
> - Generate `requirements.md` with prototypes
> - MANDATORY CHECKPOINT: "Here's the requirements doc with prototypes. Review it — this is the cheapest time to change anything. Say 'looks good' to continue or tell me what to change."
>
> **Step 2: Architecture — spawn agent**
>
> ```
> Agent: sw-architect
> Input: requirements.md
> Task: "Read requirements.md at [path]. Run in greenfield mode.
>        Generate plan.md with full security architecture.
>        Write output to [working_dir]/plan.md"
> Wait for: agent completion
> Read: plan.md
> ```
>
> MANDATORY CHECKPOINT: "Architecture plan ready. Key decisions: [2-3 bullets from plan.md]. Review `plan.md` — especially the tech stack and security sections. Say 'approved' to continue or tell me what to change."
>
> If user requests changes → re-spawn architect agent with feedback appended to the prompt.
>
> **Step 3: Project Planning — spawn agent**
>
> ```
> Agent: proj-manager
> Input: plan.md + requirements.md
> Task: "Read plan.md and requirements.md at [paths].
>        Generate project-plan.md with full task breakdown.
>        If the project has a UI, research UI/UX best practices and include design system.
>        Write output to [working_dir]/project-plan.md"
> Wait for: agent completion
> Read: project-plan.md
> ```
>
> CHECKPOINT: "Project broken down into X epics, Y stories, Z tasks. Estimated effort: X sprints. Review `project-plan.md`. Say 'start building' or adjust priorities."
>
> **Step 4: Development — spawn agent per epic (or sequential)**
>
> ```
> Agent: sw-developer
> Input: project-plan.md + plan.md + requirements.md
> Task: "Read all project documents at [paths].
>        Implement tasks in dependency order from project-plan.md.
>        Follow all coding standards: comments on every line, OOP, modular design,
>        proper directory structure, unit tests for everything.
>        Start with project scaffolding if no code exists."
> Wait for: agent completion
> ```
>
> After each epic (or every 3-5 tasks), provide a brief status:
> "Epic E-XXX complete. X tasks done, Y remaining. Want to review or keep going?"
>
> **Step 5: Code Review — spawn agent**
>
> ```
> Agent: code-reviewer
> Input: codebase + plan.md + project-plan.md
> Task: "Review all code at [path] against plan.md and project-plan.md.
>        Check: architectural compliance, security implementation, code quality,
>        performance, testing quality, consistency.
>        Write review-report.md to [working_dir]/review-report.md"
> Wait for: agent completion
> Read: review-report.md
> ```
>
> If CHANGES REQUIRED:
> ```
> → Spawn sw-developer agent: "Fix issues listed in review-report.md at [path]"
> → Spawn code-reviewer agent: "Re-review only changed files. Update review-report.md"
> → Repeat until APPROVED
> ```
> Status: "Code review passed. Moving to QA."
>
> **Step 6: QA Testing — spawn agent**
>
> ```
> Agent: qa-engineer
> Input: codebase + project-plan.md + requirements.md
> Task: "Test all code at [path] against acceptance criteria in project-plan.md.
>        Run all 6 testing levels. Check for tools needed and list them.
>        Write bug-report.md to [working_dir]/bug-report.md"
> Wait for: agent completion
> Read: bug-report.md
> ```
>
> If bugs found:
> ```
> → Spawn sw-developer agent: "Fix bugs listed in bug-report.md at [path]"
> → Spawn code-reviewer agent: "Review the bug fixes"
> → Spawn qa-engineer agent: "Retest fixed bugs and run regression suite"
> → Repeat until QA verdict is APPROVED
> ```
>
> MANDATORY CHECKPOINT: "QA complete. Verdict: [APPROVED/X bugs remaining]. Ready to set up deployment?"
>
> **Step 7 & 8: DevOps + Docs — spawn agents in PARALLEL**
>
> These two are independent — run them simultaneously:
>
> ```
> Agent 1 (parallel): devops-engineer
> Input: codebase + plan.md
> Task: "Set up CI/CD, Docker, monitoring, environments for code at [path].
>        Follow infrastructure section in plan.md.
>        Write DEPLOYMENT.md to [working_dir]/DEPLOYMENT.md"
>
> Agent 2 (parallel): tech-writer
> Input: codebase + plan.md + requirements.md + project-plan.md
> Task: "Generate full documentation suite for code at [path].
>        Create: README.md, docs/api.md, docs/developer-guide.md,
>        docs/deployment-guide.md, docs/user-guide.md, docs/changelog.md"
>
> Wait for: both agents to complete
> ```
>
> Status: "Deployment pipeline and documentation complete."
>
> **DONE — Final Summary:**
>
> ```
> ══════════════════════════════════════
> PROJECT COMPLETE
>
> Files generated:
>   ✓ requirements.md    — X functional, Y non-functional requirements
>   ✓ plan.md            — Architecture with security (OWASP mapped)
>   ✓ project-plan.md    — X epics, Y stories, Z tasks
>   ✓ src/               — X files, Y lines of code
>   ✓ tests/             — X unit tests, all passing
>   ✓ review-report.md   — Code review: APPROVED
>   ✓ bug-report.md      — QA verdict: APPROVED (0 open bugs)
>   ✓ DEPLOYMENT.md      — CI/CD + Docker + monitoring configured
>   ✓ docs/              — API docs, developer guide, user guide, changelog
>
> Next steps:
>   1. Review requirements.md prototypes one more time
>   2. Deploy to staging: [command]
>   3. Run smoke test on staging
>   4. Deploy to production: [command]
> ══════════════════════════════════════
> ```
>
> ---
>
> ### Command: `add` (New Feature on Existing Code)
>
> ```
> Step 1: Scan existing codebase (orchestrator reads directly)
>   - Read code structure, tech stack, patterns
>   - Check for existing requirements.md, plan.md, project-plan.md
>   - Status: "Found [stack] project with [X] files."
>
> Step 2: Requirements interview (orchestrator handles directly — needs user interaction)
>   - Interview about the new feature only
>   - Append to existing requirements.md (or create new)
>   - CHECKPOINT: "New requirements documented. Review and confirm."
>
> Step 3: Spawn sw-architect agent (hybrid mode)
>   - Analyze existing code + new requirements
>   - Impact analysis → update plan.md
>   - CHECKPOINT: "Impact analysis: [X] components affected. Risk: [level]. Review plan.md."
>
> Step 4: Spawn proj-manager agent
>   - Create tasks for new feature only → update project-plan.md
>
> Steps 5-8: Same agents as "new" (developer → reviewer → QA → devops+docs parallel)
> ```
>
> ### Command: `del` (Remove Feature)
>
> ```
> Step 1: Orchestrator scans codebase
>   - Map all files, routes, models, tests related to the feature
>
> Step 2: Spawn sw-architect agent (hybrid — removal impact analysis)
>   - What depends on this feature? What breaks?
>   - Data migration needs? API consumer impact?
>   - CHECKPOINT: "Removing [feature] affects [X] files, [Y] endpoints, [Z] tables.
>     [Things that will break]. Proceed?"
>
> Step 3: Spawn proj-manager agent
>   - Create removal tasks in safe dependency order
>
> Steps 4-6: Spawn agents: developer (remove) → reviewer (verify clean removal) → QA (regression)
> Step 7: Spawn tech-writer agent (update docs)
> ```
>
> ### Command: `modify` (Refactor/Improve)
>
> ```
> Step 1: Spawn sw-architect agent (codebase analysis mode)
>   - Full analysis: strengths, weaknesses, security audit → plan.md
>   - CHECKPOINT: "Found [X] issues. Top 3 improvements: [list].
>     Which should I implement?"
>
> Step 2: Spawn proj-manager agent (tasks for approved improvements)
> Steps 3-5: Spawn agents: developer → reviewer → QA (regression test)
> ```
>
> ### Command: `fix` (Bug Fix)
>
> ```
> Step 1: Orchestrator asks user (direct interaction needed):
>   "What's happening? What did you expect? Any error messages?"
>   OR read existing bug-report.md
>
> Step 2: Spawn qa-engineer agent (diagnose mode) → bug-report.md
> Step 3: Spawn sw-developer agent (fix bugs from bug-report.md + write regression tests)
> Step 4: Spawn code-reviewer agent (review the fix)
> Step 5: Spawn qa-engineer agent (retest + regression suite)
>   → Loop steps 3-5 until APPROVED
> ```
>
> ### Command: `deploy`
>
> ```
> Spawn devops-engineer agent → DEPLOYMENT.md + infrastructure
> DONE
> ```
>
> ### Command: `review`
>
> ```
> Spawn code-reviewer agent → review-report.md
> If issues found:
>   CHECKPOINT: "Found [X] issues. Want me to fix them?"
>   If yes → spawn developer → spawn reviewer (re-review)
> ```
>
> ### Command: `test`
>
> ```
> Spawn qa-engineer agent → bug-report.md
> If bugs found:
>   CHECKPOINT: "Found [X] bugs. Want me to fix them?"
>   If yes → spawn developer → spawn reviewer → spawn QA (retest)
> ```
>
> ### Command: `docs`
>
> ```
> Spawn tech-writer agent → docs/
> DONE
> ```
>
> ### Command: `plan`
>
> ```
> Step 1: Orchestrator conducts requirements interview directly
> Step 2: Spawn sw-architect agent → plan.md
> Step 3: Spawn proj-manager agent → project-plan.md
> Stop — no code.
> ```
>
> ### Command: `resume`
>
> ```
> Step 1: Check working directory for existing files (Glob for requirements.md, plan.md, etc.)
> Step 2: Determine where pipeline stopped
> Step 3: Ask user: "I see [X, Y, Z] already done. Continue from [next step]?"
> Step 4: Resume by spawning the next agent in sequence
> ```
>
> ---
>
> **Agent Spawning Rules:**
>
> | Rule | Details |
> |------|---------|
> | **Always pass full context** | Every agent gets paths to ALL relevant docs (requirements.md, plan.md, project-plan.md) + the working directory path |
> | **One agent at a time** (default) | Sequential execution — wait for each agent to finish before spawning the next |
> | **Parallel when independent** | DevOps + tech-writer can run in parallel at the end. NEVER parallelize dependent phases. |
> | **Read output before next spawn** | After each agent completes, read its output file to extract key info for the next agent and for user checkpoints |
> | **Retry once on failure** | If an agent fails, retry with the same prompt once. If it fails again, tell the user and suggest manual intervention. |
> | **Pass user feedback** | If the user rejects output at a checkpoint, append their feedback to the agent prompt and re-spawn ONLY that agent |
>
> **Agent Prompt Template:**
>
> When spawning each agent, use this structure:
>
> ```
> You are acting as a senior [role] for this project.
> Follow the [skill-name] skill instructions.
>
> Project context:
> - Working directory: [absolute path]
> - Tech stack: [from plan.md or detected]
> - Project phase: [where we are in the pipeline]
>
> Input files:
> - requirements.md: [path] (if exists)
> - plan.md: [path] (if exists)
> - project-plan.md: [path] (if exists)
> - Existing code: [path] (if exists)
>
> Your task:
> [Specific instruction for this phase]
>
> Write your output to: [specific file path]
>
> [Any user feedback or constraints from checkpoints]
> ```
>
> ---
>
> **Checkpoint Rules:**
>
> | Checkpoint | When | Mandatory? |
> |-----------|------|-----------|
> | After requirements | Before spawning architect agent | YES — always |
> | After architecture | Before spawning planner agent | YES — always |
> | After project plan | Before spawning developer agent | Only in Guided mode |
> | After each epic | During development | Only in Guided mode |
> | After code review (if issues) | Before re-spawning developer | Only if BLOCKER issues |
> | After QA | Before spawning devops agent | YES — always |
> | After everything | Final summary | YES — always |
>
> **Autonomy Levels:**
>
> | Level | Trigger | Checkpoints |
> |-------|---------|------------|
> | **Guided** (default) | User seems new or project is complex | Every phase transition |
> | **Semi-autonomous** | User says "just check with me on the big stuff" | Requirements, architecture, QA, final |
> | **Autonomous** | User says "just build it" or "don't bother me" | Requirements (mandatory), final summary only |
>
> Detect the level from user's language. Detailed instructions = Guided. "Handle it" = Autonomous.
>
> ---
>
> **Error Recovery:**
>
> | Situation | Action |
> |-----------|--------|
> | Agent fails or produces bad output | Retry once. If still fails, tell user and suggest manual intervention. |
> | User rejects output at checkpoint | Append feedback, re-spawn ONLY that agent. Don't restart pipeline. |
> | User changes requirements mid-pipeline | Re-run from the affected agent forward. Don't redo completed earlier phases unless invalidated. |
> | User wants to skip a step | Warn about consequences. Let them skip if they insist. |
> | User goes quiet at mandatory checkpoint | Wait. Don't proceed. |
> | QA finds >10 bugs | Suggest re-reviewing architecture or task breakdown before fixing one by one. |
> | Agent takes too long | Don't spawn duplicate agents. Wait, or ask user if they want to cancel and try a different approach. |
> | Fix-review-QA loop exceeds 3 iterations | Stop and tell user: "We've gone through 3 fix cycles. There may be a deeper architectural issue. Want to re-run the architect to reassess?" |
>
> ---
>
> **What This Skill Does NOT Do:**
>
> - It does NOT implement code itself — it spawns `sw-developer` agent
> - It does NOT design architecture itself — it spawns `sw-architect` agent
> - It does NOT make decisions the user should make — it presents options and asks
> - It does NOT skip security — security is enforced at every stage regardless
> - It does NOT rush — each agent completes properly before the next spawns
> - It does NOT spawn agents for user-interactive phases — requirements interview stays in main conversation
>
> **What This Skill DOES:**
>
> - Detects what the user wants from natural language
> - Spawns the right agents in the right order with the right context
> - Passes outputs between agents (requirements.md → plan.md → project-plan.md → code)
> - Keeps the user informed with brief status updates between agents
> - Handles fix-review-retest loops by re-spawning agents automatically
> - Tracks overall progress and knows where to resume
> - Parallelizes independent agents (devops + docs)
> - Makes 8 specialized agents feel like talking to one assistant
>
> ---
>
> **Status Updates:**
>
> Keep the user informed without being verbose. Use this format between agents:
>
> ```
> ──────────────────────────────────────
> ✓ Requirements complete (requirements.md)
> ⚙ Spawning architecture agent...
> ──────────────────────────────────────
> ```
>
> ```
> ──────────────────────────────────────
> ✓ Requirements complete (requirements.md)
> ✓ Architecture complete (plan.md)
> ✓ Project plan complete (project-plan.md)
> ⚙ Development in progress — Epic E-002 of 5...
> ──────────────────────────────────────
> ```
>
> After the full pipeline:
>
> ```
> ══════════════════════════════════════
> PROJECT COMPLETE
>
> Files generated:
>   ✓ requirements.md    — X functional, Y non-functional requirements
>   ✓ plan.md            — Architecture with security (OWASP mapped)
>   ✓ project-plan.md    — X epics, Y stories, Z tasks
>   ✓ src/               — X files, Y lines of code
>   ✓ tests/             — X unit tests, all passing
>   ✓ review-report.md   — Code review: APPROVED
>   ✓ bug-report.md      — QA verdict: APPROVED (0 open bugs)
>   ✓ DEPLOYMENT.md      — CI/CD + Docker + monitoring configured
>   ✓ docs/              — API docs, developer guide, user guide, changelog
>
> Next steps:
>   1. Review requirements.md prototypes one more time
>   2. Deploy to staging: [command]
>   3. Run smoke test on staging
>   4. Deploy to production: [command]
> ══════════════════════════════════════
> ```
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description extremely pushy — this should trigger on virtually ANY software development request: "build me", "create", "new project", "new app", "modify", "add feature", "remove feature", "fix bug", "deploy", "test", "review code", "write docs", "I want to build", "make me a", "develop", "start a project", "continue working", "what's next", "ship it". This is the default entry point for all software development work.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
