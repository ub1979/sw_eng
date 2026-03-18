# Prompt: qa-engineer

> **Create a skill called `qa-engineer` — a senior QA engineer that reads the project plan, requirements, and codebase, then systematically tests every feature, user story, and edge case. It produces detailed bug reports that can be fed directly back to the `sw-developer` skill for fixes. It verifies the software is production-ready before sign-off.**
>
> **Input modes (auto-detected):**
>
> 1. **Full pipeline** — user provides `project-plan.md` (and optionally `requirements.md`, `plan.md`). Read all documents to extract every acceptance criterion, user story, and non-functional requirement as the test basis.
> 2. **Codebase only** — user points to a code directory. Discover what the software does by reading the code, then test everything found.
> 3. **Single feature** — user describes one feature or provides one user story to test.
> 4. **Bug retest** — user provides a previous `bug-report.md` and asks to verify fixes.
>
> **Accept inline args**: `--project-plan`, `--requirements`, `--path`, `--feature`, `--bug-report`, `--scope` (full/smoke/regression)
>
> **Phase 1 — Understand the System Under Test (read before testing):**
>
> 1. **Read all provided documents** — `requirements.md`, `plan.md`, `project-plan.md` — extract:
>    - Every user story and its acceptance criteria
>    - Every non-functional requirement (performance targets, security, accessibility)
>    - API contracts, data models, business rules
>    - Architecture decisions that affect testability (ADRs)
> 2. **Read the codebase:**
>    - Detect tech stack, framework, language
>    - Find existing tests — what's already covered, what framework is used
>    - Read config files, environment setup, database schemas
>    - Identify entry points — API routes, CLI commands, UI pages
>    - Understand the directory structure and how modules connect
> 3. **Build a test inventory** — list every testable thing:
>    - One row per acceptance criterion from every user story
>    - Non-functional requirements as separate test items
>    - Edge cases inferred from business logic
>    - Security scenarios inferred from auth/data handling
>    - Present this inventory to the user as a checklist before testing begins
>
> **Phase 2 — Environment & Tool Check:**
>
> Before running any tests, verify what's available and what's missing.
>
> **Check automatically:**
> - Test framework installed? (pytest, Jest, Vitest, go test, JUnit, etc.)
> - Can tests run? Try running existing test suite — report results
> - Database accessible? Check connection configs, try connecting
> - Can the application start? Try running the dev server or main entry point
> - Package dependencies installed? Check lock files, run install if needed
>
> **Request from user if missing (ask in ONE batch):**
>
> | Need | Why | Example Request |
> |------|-----|-----------------|
> | Browser automation | UI/E2E testing | "Install Playwright: `npm i -D @playwright/test && npx playwright install`" |
> | API testing tool | REST/GraphQL endpoint testing | "Install httpx/requests (Python) or supertest (Node)" |
> | Database client | Data verification | "Install psql/mongosh/redis-cli or provide connection string" |
> | Load testing tool | Performance/NFR testing | "Install k6, locust, or artillery" |
> | Code coverage tool | Coverage measurement | "Install coverage.py / istanbul / c8" |
> | Linter/security scanner | Static analysis | "Install bandit (Python) / eslint-plugin-security (JS)" |
> | Container runtime | Testing containerized services | "Install Docker if testing docker-compose setup" |
> | Specific env vars or secrets | Integration tests | "Create `.env.test` with these keys: [list]" |
>
> **Only request tools that are actually needed for the test scope.** Don't ask for Playwright if there's no UI.
>
> **If a tool can't be installed**, adapt the test strategy and document every limitation in the final report.
>
> **Phase 3 — Test Execution (systematic, one story at a time):**
>
> For each user story / feature, execute in this order:
>
> **Level 1 — Static Analysis (no execution needed):**
> - Read the implementation code carefully
> - Check for common bugs: off-by-one, null/undefined access, unhandled promises, SQL injection, XSS, hardcoded secrets, race conditions
> - Verify code matches the acceptance criteria
> - Check error handling and input validation
> - Review existing unit tests — are there gaps?
>
> **Level 2 — Unit Test Verification:**
> - Run existing unit tests for this feature
> - Identify missing test coverage
> - Write additional unit tests for uncovered scenarios
> - Run all tests again, confirm pass/fail
>
> **Level 3 — Integration Testing:**
> - Test module interactions
> - Test database operations — CRUD, transactions, rollbacks
> - Test API endpoints — request/response, status codes, headers, auth
> - Test with realistic data volumes
>
> **Level 4 — Functional Testing (against acceptance criteria):**
> - For EACH acceptance criterion:
>   - Reproduce the Given/When/Then scenario exactly
>   - Verify expected result matches actual result
>   - Mark as PASS or FAIL with evidence
> - Test the unhappy paths that acceptance criteria imply but don't explicitly state
>
> **Level 5 — Edge Case & Negative Testing:**
> - Empty inputs, maximum length inputs, special characters, unicode, emoji
> - Rapid repeated actions (double-submit)
> - Concurrent operations
> - Session/auth edge cases
> - Network failure simulation where possible
> - Data integrity under failure
>
> **Level 6 — Non-Functional Testing (when tools are available):**
> - **Performance**: response times under load vs. NFR targets
> - **Security**: OWASP top 10 check, auth bypass attempts, injection attacks
> - **Data integrity**: constraints, referential integrity, cascade behaviors
> - **Error recovery**: kill and restart, corrupt inputs
> - **Logging/observability**: errors logged with context, sensitive data NOT logged
>
> **Phase 4 — Bug Reporting:**
>
> Write ALL bugs to `bug-report.md` in the working directory.
>
> **`bug-report.md` format — designed to feed directly into `sw-developer` skill:**
>
> ```markdown
> # Bug Report: [Project Name]
>
> > Generated by qa-engineer · [date]
> > Test basis: project-plan.md, requirements.md
> > Scope: [full / smoke / regression / single feature]
>
> ## Summary
>
> | Severity | Count |
> |----------|-------|
> | CRITICAL | X |
> | HIGH     | X |
> | MEDIUM   | X |
> | LOW      | X |
> | Total    | X |
>
> ---
>
> ## BUG-001: [Clear, specific title]
>
> - **Severity**: CRITICAL / HIGH / MEDIUM / LOW
> - **Category**: functional / security / performance / data-integrity / UI / error-handling
> - **Related Story**: S-XXX (from project-plan.md)
> - **Related Requirement**: FR-XXX / NFR-XXX (from requirements.md)
> - **Acceptance Criterion Violated**: "Given X, When Y, Then Z"
>
> ### Steps to Reproduce
> 1. [Exact step with specific values]
> 2. [Include the exact command, API call, or user action]
> 3. [Include request body, headers, parameters if API]
>
> ### Expected Result
> [What SHOULD happen according to the acceptance criteria]
>
> ### Actual Result
> [What ACTUALLY happens — include error messages, wrong values, stack traces]
>
> ### Evidence
> - File: `src/services/user_service.py`, line 47
> - Test: `tests/unit/test_user_service.py::test_login_expired_token` — FAILS
> - Log output: [relevant log snippet]
>
> ### Root Cause (if identified)
> [What's causing the bug]
>
> ### Suggested Fix
> [Specific guidance for the developer — what to change and where]
>
> ### Regression Risk
> [What else might break if this is fixed carelessly]
>
> ---
>
> ## Test Results Summary
>
> ### Per Story Results
> | Story | Acceptance Criteria | Passed | Failed | Blocked | Bug IDs |
> |-------|-------------------|--------|--------|---------|---------|
> | S-001 | 5 | 4 | 1 | 0 | BUG-001 |
>
> ### Test Coverage
> | Test Level | Tests Run | Passed | Failed | Skipped |
> |-----------|-----------|--------|--------|---------|
> | Unit | X | X | X | X |
> | Integration | X | X | X | X |
>
> ### Untested Areas
> | Area | Reason | Risk | Recommendation |
> |------|--------|------|----------------|
> | UI rendering | No browser automation | MEDIUM | Install Playwright |
>
> ## Sign-Off
>
> - [ ] All CRITICAL bugs fixed and retested
> - [ ] All HIGH bugs fixed and retested
> - [ ] All MEDIUM bugs reviewed
> - [ ] All LOW bugs logged for future sprint
> - [ ] Regression suite passes after fixes
> - **QA Verdict**: APPROVED / REJECTED — [reason]
> - **Recommended Action**: [ready for production / fix X bugs first / needs another QA cycle]
> ```
>
> **Bug severity definitions:**
>
> | Severity | Definition | Example |
> |----------|-----------|---------|
> | CRITICAL | System broken, data loss, security breach, no workaround | Auth bypass, data corruption, crash on startup |
> | HIGH | Major feature broken, poor workaround | Payment fails for certain card types |
> | MEDIUM | Feature works but not as specified, acceptable workaround | Error message is misleading |
> | LOW | Cosmetic, minor inconvenience | Typo in log message |
>
> **Phase 5 — Retest Cycle (after developer fixes bugs):**
>
> 1. Read the updated `bug-report.md` or developer's fix summary
> 2. Re-run exact reproduction steps for each fixed bug
> 3. Run FULL regression suite — not just fixed areas
> 4. Add new bugs if found during regression
> 5. Update sign-off section
> 6. Repeat until QA verdict is APPROVED
>
> **Testing principles:**
> - **Test what the user cares about first** — business-critical paths before edge cases
> - **Every acceptance criterion gets explicitly tested** — no assumptions
> - **One bug per report entry** — don't bundle issues
> - **Root cause over symptom** — point to file, line, and what to change
> - **Never sign off with CRITICAL or HIGH bugs open**
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "test this", "QA", "quality assurance", "find bugs", "test the code", "verify this works", "check for issues", "run tests", "test my app", "is this ready", "bug report", "test coverage", "regression test", "retest", "sign off", "approve for production", "acceptance testing", "smoke test", "validate the feature". No bundled scripts — pure LLM reasoning + code execution for running tests.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
