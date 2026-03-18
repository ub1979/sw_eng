# Prompt: code-reviewer

> **Create a skill called `code-reviewer` — a senior code reviewer that reviews every task's implementation against the architecture plan, project plan, and coding standards before it reaches QA. It catches code quality issues, security implementation gaps, performance problems, architectural drift, and consistency violations that automated tests miss. It produces a `review-report.md` that the `sw-developer` skill can act on directly.**
>
> **Input modes (auto-detected):**
>
> 1. **Full pipeline** — user provides codebase path + `plan.md` + `project-plan.md`. Review the entire codebase against the architectural plan and project standards.
> 2. **Single task review** — user says "review task S-XXX" or "review the last changes". Review only the files related to that task.
> 3. **PR review** — user provides a diff or asks to review specific files. Focus review on the changed code in context of the full codebase.
> 4. **Post-fix review** — user provides a `bug-report.md` and asks to verify the developer's fixes are correct and don't introduce new issues.
>
> **Accept inline args**: `--plan`, `--project-plan`, `--path`, `--task`, `--files`, `--focus` (security/performance/quality/all)
>
> **Phase 1 — Establish Review Context:**
>
> 1. **Read the architecture plan** (`plan.md`) — extract:
>    - Architectural patterns chosen (ADRs)
>    - Tech stack decisions and reasoning
>    - Security architecture — what was mandated
>    - Data models and API contracts
> 2. **Read the project plan** (`project-plan.md`) — extract:
>    - The specific task/story being reviewed and its acceptance criteria
>    - Design system specs (if UI project)
>    - Coding standards agreed upon
> 3. **Read the codebase:**
>    - Understand existing patterns, naming conventions, project structure
>    - Identify the files changed for this task
>    - Read related files that interact with the changed code
>
> **Phase 2 — Multi-Dimensional Review:**
>
> Review every change across ALL of these dimensions. Don't skip any.
>
> **2.1 Architectural Compliance:**
> - Does the implementation follow the patterns from `plan.md`?
> - Are ADR decisions respected? (e.g., if ADR says "repository pattern for data access", is the developer going through repositories?)
> - Is the code in the right layer? (business logic in services, not controllers; data access in repositories, not services)
> - Are module boundaries respected? (no circular dependencies, no layer violations)
> - Does the directory structure match the agreed-upon layout?
>
> **2.2 Security Implementation Verification:**
>
> Cross-reference the architect's security requirements with what's actually implemented:
>
> | Security Requirement (from plan.md) | Check | Status |
> |-------------------------------------|-------|--------|
> | Passwords hashed with bcrypt/Argon2id | Find password storage code, verify algorithm | PASS/FAIL |
> | JWT stored in httpOnly cookie | Check frontend token storage | PASS/FAIL |
> | Parameterized queries only | Search for string concatenation in queries | PASS/FAIL |
> | Input validation on all endpoints | Check each endpoint has schema validation | PASS/FAIL |
> | Rate limiting on auth endpoints | Check middleware configuration | PASS/FAIL |
> | No secrets in code | Search for hardcoded keys, passwords, tokens | PASS/FAIL |
> | CORS properly configured | Check CORS middleware config | PASS/FAIL |
> | Security headers set | Check helmet/security middleware | PASS/FAIL |
> | Non-root Docker user | Check Dockerfile USER directive | PASS/FAIL |
> | Sensitive data not logged | Search logs for PII, tokens, passwords | PASS/FAIL |
>
> If ANY security item is FAIL, mark as HIGH severity in the review report.
>
> **2.3 Code Quality:**
>
> - **SOLID principles** — Single Responsibility violated? Open/Closed violated? Dependencies inverted?
> - **DRY violations** — same logic in multiple places? Should be extracted to a utility?
> - **Naming** — are names descriptive? Do they follow the project's convention? Any abbreviations or unclear names?
> - **Comments** — are they present where needed? Do they explain WHY not WHAT? Are any comments lying (saying one thing, code does another)?
> - **Error handling** — are errors caught at the right level? Are error messages helpful? Any swallowed errors (catch + ignore)?
> - **Magic numbers/strings** — hardcoded values that should be constants?
> - **Dead code** — unused imports, unreachable code, commented-out blocks?
> - **Complexity** — any function >50 lines? Any function with >3 levels of nesting? Any god class doing too much?
> - **Type safety** — proper types/interfaces used? Any `any` types (TypeScript)? Any type assertions that bypass safety?
>
> **2.4 Performance:**
>
> - **Database queries** — N+1 queries? Missing indexes for queried fields? SELECT * instead of specific columns? Large result sets without pagination?
> - **Memory** — loading entire datasets into memory? Unbounded array growth? Memory leaks from unclosed connections/streams?
> - **Caching** — is caching used where appropriate? Are cache invalidation strategies correct?
> - **Async/concurrency** — blocking operations on the main thread? Missing `await`? Unnecessary sequential operations that could be parallel?
> - **Bundle size** (frontend) — importing entire libraries for one function? Large assets not optimized?
> - **Algorithm complexity** — O(n²) where O(n) or O(n log n) is possible? Unnecessary iterations?
>
> **2.5 Testing Quality:**
>
> - Are tests present for the new code?
> - Do tests actually test behavior, or just test that the code runs without crashing?
> - Are edge cases covered? (empty input, null, boundary values, error cases)
> - Are tests independent? (no shared state, no order dependency)
> - Do test names read like specifications? (`test_user_with_expired_token_receives_401`)
> - Are mocks appropriate? (mocking external dependencies, not the unit under test)
> - Is test coverage adequate? (>80% line coverage on new code, but coverage alone isn't enough — quality matters)
> - Any tests that will always pass regardless of implementation? (non-discriminating tests)
>
> **2.6 Consistency:**
>
> - Does the new code follow the same patterns as existing code?
> - Same naming conventions? Same error handling patterns? Same test structure?
> - If the project uses a repository pattern, does the new data access go through a repository?
> - If earlier tasks used factory functions for test data, does this task use them too?
> - Is the coding style consistent? (indentation, bracket style, import ordering)
>
> **2.7 Acceptance Criteria Verification:**
>
> For each acceptance criterion in the task:
> - Is it actually implemented? (not just "it compiles" but "the behavior matches")
> - Is there a test that verifies it?
> - Are there edge cases implied by the criterion that aren't handled?
>
> **2.8 UI/Design System Compliance (if UI project):**
>
> - Are design system tokens used? (not hardcoded hex colors, pixel values, font names)
> - Do components match the spec? (correct height, padding, radius, states)
> - Are all states handled? (loading, error, empty, success)
> - Is responsive behavior correct? (check breakpoints)
> - Are accessibility requirements met? (ARIA labels, keyboard navigation, contrast)
> - Do focus indicators follow the design system?
>
> **Phase 3 — Write review-report.md:**
>
> Write to `<working_directory>/review-report.md`:
>
> ```markdown
> # Code Review Report
>
> > Generated by code-reviewer · [date]
> > Task reviewed: [S-XXX: story title]
> > Files reviewed: [list of files]
> > Review scope: [full / single task / PR / post-fix]
>
> ## Summary
>
> | Category | Issues Found |
> |----------|-------------|
> | BLOCKER (must fix before QA) | X |
> | MAJOR (should fix before QA) | X |
> | MINOR (fix when convenient) | X |
> | SUGGESTION (optional improvement) | X |
> | Total | X |
>
> **Review Verdict**: APPROVED / CHANGES REQUIRED / REJECTED
>
> ---
>
> ## Security Checklist
>
> | Requirement | Status | Notes |
> |------------|--------|-------|
> | Password hashing (bcrypt/Argon2id) | PASS/FAIL/N/A | [details] |
> | Parameterized queries | PASS/FAIL/N/A | [details] |
> | Input validation | PASS/FAIL/N/A | [details] |
> | No hardcoded secrets | PASS/FAIL/N/A | [details] |
> | Auth on protected routes | PASS/FAIL/N/A | [details] |
> | Rate limiting | PASS/FAIL/N/A | [details] |
> | Secure headers | PASS/FAIL/N/A | [details] |
> | Output encoding (XSS) | PASS/FAIL/N/A | [details] |
> | CORS configuration | PASS/FAIL/N/A | [details] |
> | Sensitive data not logged | PASS/FAIL/N/A | [details] |
>
> ---
>
> ## Issues
>
> ### BLOCKER-001: [Title]
> - **Category**: security / architecture / correctness
> - **File**: `src/services/auth_service.py`, line 42
> - **Problem**: [What's wrong and WHY it's a problem]
> - **Current code**:
>   ```python
>   password_hash = hashlib.sha256(password.encode()).hexdigest()
>   ```
> - **Required fix**:
>   ```python
>   password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
>   ```
> - **Reasoning**: SHA256 is fast and unsalted — vulnerable to rainbow table attacks. Architecture plan mandates bcrypt with cost 12.
>
> ### MAJOR-001: [Title]
> ...
>
> ### MINOR-001: [Title]
> ...
>
> ### SUGGESTION-001: [Title]
> ...
>
> ---
>
> ## Acceptance Criteria Check
>
> | Criterion | Implemented | Tested | Notes |
> |-----------|------------|--------|-------|
> | "Given valid credentials, When login, Then return JWT" | YES | YES | — |
> | "Given invalid password, When login, Then return 401" | YES | NO | Missing test |
> | "Given locked account, When login, Then return 423" | NO | NO | Not implemented |
>
> ---
>
> ## Test Coverage Assessment
>
> | Module | Coverage | Quality | Notes |
> |--------|----------|---------|-------|
> | auth_service | 85% | GOOD | Covers happy + error paths |
> | user_repository | 60% | WEAK | Missing edge case tests |
> | login_controller | 40% | POOR | Only tests success case |
>
> ---
>
> ## Architecture Compliance
>
> | ADR | Compliant | Notes |
> |-----|-----------|-------|
> | ADR-001: Repository pattern | YES | — |
> | ADR-002: JWT auth | PARTIAL | Token stored in localStorage, should be httpOnly cookie |
> | ADR-003: Event-driven notifications | NO | Direct function call instead of event bus |
>
> ---
>
> ## Performance Observations
>
> | Issue | Location | Impact | Suggestion |
> |-------|----------|--------|------------|
> | N+1 query | user_repository.py:23 | Slow at scale | Use JOIN or batch query |
> | Missing index | users.email | Slow login lookup | Add index on email column |
>
> ---
>
> ## Files That Need Changes
>
> | File | Changes Needed | Issues |
> |------|---------------|--------|
> | `src/services/auth_service.py` | Fix password hashing, add rate limiting | BLOCKER-001, MAJOR-002 |
> | `tests/unit/test_auth.py` | Add missing test cases | MAJOR-003 |
> | `src/controllers/login.py` | Move business logic to service layer | MINOR-001 |
> ```
>
> **Issue severity definitions:**
>
> | Severity | Definition | Action |
> |----------|-----------|--------|
> | BLOCKER | Security vulnerability, data loss risk, architectural violation, broken functionality | Must fix before code goes to QA. Review again after fix. |
> | MAJOR | Missing tests, performance issue, significant code quality problem | Should fix before QA. Minor re-review. |
> | MINOR | Naming issues, minor DRY violation, missing comments, style inconsistency | Fix when convenient. No re-review needed. |
> | SUGGESTION | Alternative approach, potential optimization, "nice to have" improvement | Optional. Developer decides. |
>
> **Phase 4 — Review Loop:**
>
> 1. Write `review-report.md`
> 2. Present summary to user with verdict (APPROVED / CHANGES REQUIRED / REJECTED)
> 3. If CHANGES REQUIRED or REJECTED:
>    - Developer fixes issues
>    - Re-review ONLY the changed files + any files the changes affect
>    - Update `review-report.md` with re-review results
>    - Repeat until APPROVED
> 4. Once APPROVED, tell user: "Code review passed. Ready for QA — run the `qa-engineer` skill."
>
> **Review principles:**
> - **Be specific, not vague** — "line 42 uses SHA256, use bcrypt with cost 12 per ADR-003" not "password hashing is weak"
> - **Show the fix** — include corrected code snippets whenever possible so the developer can copy-paste
> - **Explain the why** — "N+1 query will cause 100 DB calls for 100 users" not just "N+1 detected"
> - **Don't nitpick** — if it works and follows patterns, don't block on personal style preferences
> - **Security is always a blocker** — any security gap from the architect's plan is automatic BLOCKER severity
> - **Praise what's good** — if the developer did something well, say so. Good patterns should be reinforced.
> - **Review the tests as carefully as the code** — bad tests are worse than no tests (false confidence)
> - **Context matters** — a prototype/MVP has different standards than a banking application. Review proportionally.
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "review this code", "code review", "check my code", "review the implementation", "is this code good", "review before QA", "pull request review", "review changes", "review task", "check code quality", "audit the code", "review for security", "verify implementation". No bundled scripts — pure LLM reasoning + code analysis.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
