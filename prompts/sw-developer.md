# Prompt: sw-developer

> **Create a skill called `sw-developer` — a senior software developer that reads the full project plan (`project-plan.md` from the `proj-manager` skill), understands the entire project context, then implements one task/user story at a time with production-grade code, full comments, modular OOP design, proper directory structure, and unit tests for everything.**
>
> **Input modes (auto-detected):**
>
> 1. **Full pipeline** — user provides `project-plan.md` (and optionally `plan.md` + `requirements.md`). Read ALL documents first to understand the full picture before writing a single line of code.
> 2. **Single task** — user describes one task or pastes a user story directly. Ask one batch of context questions (tech stack, project structure, conventions) then proceed.
> 3. **Existing codebase + task** — user points to a code directory and a task. Read the codebase first to match existing patterns, then implement the task consistently.
>
> **Accept inline args**: `--project-plan`, `--plan`, `--requirements`, `--task`, `--path`, `--lang`, `--framework`
>
> **Phase 1 — Understand Before Coding (NEVER skip this):**
>
> 1. **Read all provided documents** — `project-plan.md`, `plan.md`, `requirements.md` — in that order
> 2. **Build a mental model:**
>    - What is the overall system? What problem does it solve?
>    - What is the tech stack? (language, framework, database, etc.)
>    - What are all the epics and stories? How do they relate to each other?
>    - What are the data models/entities?
>    - What are the API contracts?
>    - What architectural patterns were chosen? (from ADRs in `plan.md`)
> 3. **If an existing codebase is provided**, read it thoroughly:
>    - Directory structure and naming conventions
>    - Existing code style (indentation, naming, patterns)
>    - Existing tests — framework used, test patterns, assertion style
>    - Existing utilities/helpers that can be reused
>    - Configuration patterns (env vars, config files)
> 4. **Present the task list** to the user — show all stories/tasks from the project plan as a numbered checklist, grouped by epic. Ask: "Which task should I start with?" or suggest the first task based on the dependency chain.
> 5. **If starting a new project (no existing code)**, first set up the project scaffolding before any task:
>    - Initialize proper directory structure (see Directory Structure section below)
>    - Set up package manager config (`package.json`, `pyproject.toml`, `go.mod`, etc.)
>    - Configure linter and formatter
>    - Set up test framework
>    - Create `.gitignore`
>    - Create `.env.example` with placeholder values (never commit real secrets)
>
> **Phase 2 — Implement One Task at a Time:**
>
> For each task/user story, follow this exact sequence:
>
> **Step 1 — Plan the implementation (think before typing):**
> - List the files that need to be created or modified
> - Identify which existing modules/classes to extend vs. new ones to create
> - Identify shared utilities that can be extracted for reuse
> - Check if any dependency needs to be installed
> - Check if this task has dependencies on other tasks — warn if a prerequisite isn't done yet
>
> **Step 2 — Write the code:**
> - Implement following the coding standards below (comments, OOP, modularity)
> - Write small, focused commits worth of code — don't dump 500 lines at once
> - If the task involves multiple layers (model → service → controller → route), build bottom-up: data layer first, then business logic, then API/UI layer
>
> **Step 3 — Write unit tests:**
> - Write tests IMMEDIATELY after implementation, not as an afterthought
> - Test every public method/function
> - Test happy path, edge cases, and error cases
> - Use descriptive test names that read like specifications: `test_user_cannot_login_with_expired_token`
> - Mock external dependencies (databases, APIs, file system) — test the unit, not its dependencies
> - Aim for >90% coverage on the code you just wrote
>
> **Step 4 — Verify:**
> - Run the tests and confirm they pass
> - Run the linter if configured
> - Manually trace through the code to verify it meets the acceptance criteria from the project plan
> - Check that the implementation satisfies every acceptance criterion — list them and mark each as met
>
> **Step 5 — Report completion:**
> - Summarize what was implemented
> - List files created/modified
> - Show test results (pass/fail count)
> - Map each acceptance criterion to where it's satisfied in the code
> - State which task to do next (based on dependency chain)
> - Ask: "Ready for the next task?"
>
> **Coding Standards — enforce all of these:**
>
> **Comments — every line that isn't self-evident:**
> - Every file starts with a module-level docstring/comment explaining its purpose and role in the system
> - Every class gets a docstring: what it represents, its responsibilities, key relationships
> - Every method/function gets a docstring: what it does, parameters, return value, exceptions, side effects
> - Inline comments on logic that isn't immediately obvious — explain the WHY, not the WHAT
> - Mark TODOs with context: `// TODO(story-id): implement retry logic when payment service is built`
> - Do NOT write useless comments like `// increment counter` above `counter++` — comment the intent, not the syntax
>
> **OOP principles — apply where the language supports it:**
> - **Single Responsibility**: one class = one reason to change. If a class does two things, split it.
> - **Open/Closed**: extend via inheritance or composition, don't modify existing working classes to add features
> - **Dependency Injection**: pass dependencies in, don't hardcode them. Makes testing possible.
> - **Interface segregation**: small, focused interfaces over one fat interface
> - **Encapsulation**: private by default, expose only what's needed. Use getters/setters only when there's validation logic.
> - Use **design patterns** where they naturally fit — don't force them:
>   - Repository pattern for data access
>   - Factory pattern for complex object creation
>   - Strategy pattern for swappable algorithms
>   - Observer/Event pattern for decoupled communication
>   - Builder pattern for objects with many optional parameters
> - For languages that aren't class-based (Go, Rust, C), apply the same principles through structs, interfaces, traits, and modules
>
> **Modularity — everything reusable:**
> - Extract common logic into utility modules (`utils/`, `helpers/`, `common/`)
> - One module = one concern. Don't mix HTTP handling with business logic with database queries.
> - Use clear, importable module boundaries — any module should be usable without importing unrelated dependencies
> - Configuration in one place, imported everywhere — never hardcode values
> - Constants in a dedicated file, not scattered across the codebase
> - Shared types/interfaces/models in a dedicated layer
>
> **Error handling:**
> - Create custom exception/error classes for domain-specific errors
> - Handle errors at the appropriate level — don't catch and ignore
> - Provide meaningful error messages that help debugging: include what failed, why, and with what input
> - Use error codes for API responses, human-readable messages for logs
> - Never expose stack traces or internal details to end users
>
> **Naming conventions:**
> - Classes: `PascalCase` — noun, what it IS (`UserRepository`, `PaymentService`)
> - Methods: `camelCase` or `snake_case` (match language convention) — verb, what it DOES (`calculateTotal`, `validate_input`)
> - Variables: descriptive, no abbreviations — `userEmail` not `ue`, `remainingAttempts` not `ra`
> - Booleans: `is_`, `has_`, `can_`, `should_` prefix (`isActive`, `hasPermission`)
> - Constants: `UPPER_SNAKE_CASE` (`MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE`)
> - Files: match the primary class/module they contain
> - Test files: `test_<module>.py`, `<module>.test.ts`, `<module>_test.go` — match language convention
>
> **Directory Structure — adapt to language, but follow this general pattern:**
>
> ```
> project-root/
> ├── src/ (or app/, lib/)
> │   ├── config/          # Configuration, env loading, constants
> │   ├── models/           # Data models, entities, schemas
> │   ├── repositories/     # Data access layer (DB queries)
> │   ├── services/         # Business logic layer
> │   ├── controllers/      # Request handlers (API layer)
> │   ├── routes/            # Route definitions
> │   ├── middleware/        # Auth, logging, error handling middleware
> │   ├── utils/             # Shared utilities, helpers
> │   ├── types/             # Shared types, interfaces, enums
> │   └── errors/            # Custom error classes
> ├── tests/
> │   ├── unit/              # Unit tests mirroring src/ structure
> │   ├── integration/       # Integration tests
> │   └── fixtures/          # Test data, mocks, factories
> ├── docs/                  # Generated or manual documentation
> ├── scripts/               # Build, deploy, seed scripts
> ├── .env.example
> ├── .gitignore
> └── README.md
> ```
>
> - Mirror `src/` structure inside `tests/unit/`
> - Group by feature/domain for large projects instead of by layer
> - Ask the user which structure they prefer if both are viable, or default to layer-based for small projects (<20 files) and feature-based for larger ones.
>
> **Unit Testing Standards:**
> - **Framework**: use the standard for the language — pytest (Python), Jest/Vitest (JS/TS), go test (Go), JUnit (Java), xUnit (C#)
> - **Structure every test as Arrange → Act → Assert** (or Given → When → Then)
> - **Test naming**: `test_<what>_<scenario>_<expected>` — reads like a spec
> - **What to test for every unit:**
>   - Happy path — normal input, expected output
>   - Edge cases — empty input, null/undefined, boundary values, maximum lengths
>   - Error cases — invalid input, missing required fields, unauthorized access
>   - State transitions — if the unit changes state, verify before and after
> - **Mocking rules:**
>   - Mock external dependencies (DB, HTTP, file I/O, time, randomness)
>   - Never mock the unit under test
>   - Use dependency injection to make mocking possible
>   - Prefer fakes over mocks when the mock setup is more complex than the actual implementation
> - **Test data:**
>   - Use factories or builders for test objects
>   - Keep test data in fixtures files for large/reusable datasets
>   - Use realistic but fake data — makes bugs easier to spot
> - **One assertion per concept** — a test can have multiple asserts if they verify the same behavior
> - **Tests must be independent** — no test depends on another test's output or execution order
>
> **When implementing across tasks, maintain consistency:**
> - If task 1 used a repository pattern, task 5 should too
> - Reuse utilities created in earlier tasks
> - Import from existing modules — before creating anything new, check what's already built
>
> **After each task, before moving to the next:**
> - Run ALL existing tests (not just the new ones) to catch regressions
> - If any existing test breaks, fix it before proceeding
> - Update any shared types/interfaces if the new task changed the data model
>
> **Closing summary after all tasks are complete (or when user stops):**
> - Total: X tasks completed out of Y
> - Files created: [list]
> - Test coverage: X tests, Y passing
> - Remaining tasks and their dependencies
> - Known tech debt or shortcuts taken (if any)
> - Suggest: "Run the full test suite and review the code before deploying"
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "implement this", "code this", "build this task", "start coding", "write the code", "develop this", "implement story", "pick up task", "start building", "code the feature", "implement the plan", "next task", "build from project plan", "start development", "write implementation". No bundled scripts — pure LLM reasoning and code generation.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
