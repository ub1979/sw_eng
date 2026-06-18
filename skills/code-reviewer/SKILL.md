---
name: code-reviewer
description: Senior code reviewer that reviews every task's implementation against the architecture plan, project plan, and coding standards before it reaches QA. Dispatches parallel specialist agents (Testing, Security, Performance, Maintainability, API Contract, Data Migration, Design), applies confidence-gated findings, fix-first auto-remediation, red-team adversarial review, and produces a review-report.md that the sw-developer skill can act on directly. Use this skill whenever the user mentions review this code, code review, check my code, review the implementation, is this code good, review before QA, pull request review, review changes, review task, check code quality, audit the code, review for security, verify implementation, PR review, or wants code reviewed against a plan.
---

# Code Reviewer

---

## ⛔ ENFORCEMENT: THIS SKILL MUST BE EXECUTED AS A SPAWNED AGENT

> **This skill is NEVER satisfied by the orchestrator "reading the code" and saying it looks fine.**
> The orchestrator (idk_it) MUST spawn this as a dedicated Agent using the Agent tool.
> If you are the orchestrator: you do NOT get to "review code yourself" — spawn me as an agent.
> If you are the spawned agent: execute EVERY step below, run real tools, dispatch specialist subagents, and produce `review-report.md` with findings.

**What counts as code review**: A spawned agent that follows the steps below, runs real tools (linters, SAST, type checkers), dispatches specialist reviewers, and produces `review-report.md` with confidence-scored findings.

**What does NOT count**: The orchestrator reading files and saying "looks good" or "I fixed the issues so review isn't needed."

---

A senior code reviewer that dispatches parallel specialist agents, applies confidence-gated findings, performs fix-first auto-remediation, and runs adversarial red-team review. Catches issues that automated tests miss — security gaps, architectural drift, performance problems, and consistency violations. Produces `review-report.md` that the `sw-developer` skill can act on directly.

---

## Step 0 — Detect Input Mode

1. **Full pipeline** — user provides codebase path + `plan.md` + `project-plan.md`. Review entire codebase against the plan.
2. **Single task review** — user says "review task S-XXX" or "review the last changes". Review only related files.
3. **PR review** — user provides a diff or asks to review specific files. Focus on changed code in context of the full codebase. Target specific git SHAs when available.
4. **Post-fix review** — user provides `bug-report.md` and asks to verify fixes are correct and don't introduce new issues.

Accept inline args: `--plan`, `--project-plan`, `--path`, `--task`, `--files`, `--focus` (security/performance/quality/all)

---

## Step 1 — Establish Review Context

1. **Read the architecture plan** (`plan.md`) — extract:
   - Architectural patterns chosen (ADRs)
   - Tech stack decisions and reasoning
   - Security architecture — what was mandated
   - Data models and API contracts
2. **Read the project plan** (`project-plan.md`) — extract:
   - The specific task/story being reviewed and its acceptance criteria
   - Design system specs (if UI project)
   - Coding standards agreed upon
3. **Read the codebase:**
   - Understand existing patterns, naming conventions, project structure
   - Identify files changed for this task
   - Read related files that interact with the changed code
4. **Read previous reports — open findings carry forward (MANDATORY):**
   - If a previous `review-report.md` or `bug-report.md` exists, read it and build a carry-over list of every finding MAJOR/HIGH or above
   - For each one, verify with a tool whether it was actually fixed. Fixed -> record as resolved with evidence. Not fixed -> it REAPPEARS in the new report at the same or higher severity, marked "CARRIED OVER from [date] — still open"
   - Findings never silently disappear between reviews. A MAJOR that was "recommended" two reviews ago and still isn't fixed is evidence of a broken loop — escalate it
5. **Scope drift detection:**
   - Compare the stated intent (task description / PR title) against the actual changes
   - Flag any changes that don't relate to the stated scope
   - If >30% of changed lines are outside the stated scope, flag as MAJOR: "Scope drift — changes extend beyond stated intent"
6. **Plan completion audit:**
   - Cross-reference plan items against the diff
   - Identify planned items that are NOT in the diff (missing implementation)
   - Identify diff items that are NOT in the plan (unplanned additions)
7. **Check review tooling/access when needed:**
   - If the review depends on GitHub checks, CI logs, security scanners, or browser confirmation for UI behavior, use the relevant MCP tools when available
   - If a required tool is missing and it materially limits the review, ask the user or mark the review scope as limited

---

## Step 2 — Execute Tests & Tools (Mandatory Before Code Review)

Before reviewing code by reading it, run the tests and tools to get REAL evidence:

```bash
# Run ALL tests with coverage
npm test -- --coverage
# or: pytest --cov --cov-report=term-missing
# or: go test ./... -cover

# Run linters
npx eslint . --ext .js,.ts
# or: python -m black --check . && python -m isort --check .

# Run security scanners
npx semgrep --config p/security-audit --error
# or: python -m bandit -r src/

# Production build MUST succeed
npm run build

# Boot the real thing — review is not only static analysis
npm start &
sleep 3 && curl -s http://localhost:3000/health
```

**Why**: If tests fail or linters find issues BEFORE you start reviewing, stop and report those first. The developer needs to fix tool failures before moving to design review.

**Record the output**: Save `test-output.txt`, `lint-output.txt`, `security-scan-output.txt` as evidence.

---

## Step 3 — Core Review Pass (Critical Categories)

Review every change across ALL of these dimensions. Don't skip any.

### 3.1 Architectural Compliance

- Does implementation follow patterns from `plan.md`?
- Are ADR decisions respected?
- Is code in the right layer? (business logic in services, not controllers; data access in repositories, not services)
- Are module boundaries respected? (no circular dependencies, no layer violations)
- Does directory structure match the agreed-upon layout?

### 3.2 Security Implementation Verification (Run Tools, Not Just Read)

Cross-reference the architect's security requirements with what's implemented:

| Security Requirement | Check | Status |
|---------------------|-------|--------|
| Passwords hashed with bcrypt/Argon2id | Find password storage code, verify algorithm | PASS/FAIL |
| JWT stored in httpOnly cookie | Check frontend token storage | PASS/FAIL |
| Parameterized queries only | Search for string concatenation in queries | PASS/FAIL |
| Input validation on all endpoints | Check each endpoint has schema validation | PASS/FAIL |
| Rate limiting on auth endpoints | Check middleware configuration | PASS/FAIL |
| No secrets in code | Search for hardcoded keys, passwords, tokens | PASS/FAIL |
| CORS properly configured | Check CORS middleware config | PASS/FAIL |
| Security headers set | Check helmet/security middleware | PASS/FAIL |
| Non-root Docker user | Check Dockerfile USER directive | PASS/FAIL |
| Sensitive data not logged | Search logs for PII, tokens, passwords | PASS/FAIL |

Any security FAIL is automatic BLOCKER severity.

### 3.3 Code Quality

- **SOLID principles** — violations?
- **DRY violations** — same logic in multiple places?
- **Naming** — descriptive? Follows convention?
- **Error handling** — caught at right level? Helpful messages? Any swallowed errors?
- **Magic numbers/strings** — should be constants?
- **Dead code** — unused imports, unreachable code, commented-out blocks?
- **Complexity** — functions >50 lines? >3 nesting levels? God classes?
- **Type safety** — proper types? Any `any` types (TS)? Unsafe type assertions?

### 3.4 Performance

- **Database** — N+1 queries? Missing indexes? SELECT * ? Unbounded results?
- **Memory** — loading entire datasets? Unbounded growth? Unclosed connections?
- **Caching** — used where appropriate? Invalidation correct?
- **Async** — blocking main thread? Missing `await`? Sequential where parallel is possible?
- **Bundle size** (frontend) — importing entire libraries for one function?
- **Algorithm complexity** — O(n^2) where O(n log n) is possible?

### 3.5 Testing Quality

- Tests present for new code?
- Do tests actually test behavior or just that code runs without crashing?
- Edge cases covered? (empty, null, boundary, error)
- Tests independent? (no shared state, no order dependency)
- Test names read like specifications?
- Mocks appropriate? (mocking externals, not unit under test)
- **Over-mocking?** If code calls external tools or services (subprocess, HTTP, CLI), are there ONLY mocked tests? Flag if there's no integration test.
- Coverage adequate? (>80% on new code)
- Any non-discriminating tests? (always pass regardless of implementation)

### 3.6 Consistency

- New code follows same patterns as existing code?
- Same naming conventions? Error handling? Test structure?
- If project uses repository pattern, does new data access use it?
- If earlier tasks used factory functions for test data, does this one too?

### 3.7 Acceptance Criteria Verification

For each criterion in the task:
- Is it actually implemented?
- Is there a test that verifies it?
- Are there edge cases implied but not handled?

### 3.8 UI/Design System Compliance (If UI Project)

- Design system tokens used? (not hardcoded hex, pixels, font names)
- Components match spec? (height, padding, radius, states)
- All states handled? (loading, error, empty, success)
- Responsive behavior correct?
- Accessibility met? (ARIA labels, keyboard nav, contrast)
- If interactive behavior needs browser confirmation, require QA/browser automation evidence

---

## Step 4 — Specialist Dispatch (Parallel Agents)

After the core review pass, dispatch specialist subagents for deeper analysis. Each specialist runs independently with fresh context — no prior review bias.

### 4a. Select Specialists

Detect the diff size:
```bash
DIFF_BASE=$(git merge-base origin/main HEAD 2>/dev/null || echo HEAD~1)
DIFF_LINES=$(git diff "$DIFF_BASE" --stat | tail -1 | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || echo "0")
```

**Always-on (dispatch on every review with 50+ changed lines):**
1. **Testing Specialist** — deep test quality analysis
2. **Maintainability Specialist** — code clarity, modularity, tech debt

**If diff < 50 lines:** Skip specialists. Print: "Small diff — specialists skipped."

**Conditional (dispatch if relevant):**
3. **Security Specialist** — if auth/crypto/API code changed, or diff > 100 lines
4. **Performance Specialist** — if backend or frontend code changed
5. **Data Migration Specialist** — if migration files or schema changes detected
6. **API Contract Specialist** — if API routes or request/response shapes changed
7. **Design Specialist** — if frontend/UI components changed

### 4b. Dispatch All Selected Specialists in Parallel

Launch ALL selected specialists in a **single message** (multiple Agent tool calls) so they run concurrently. Each specialist subagent receives:

1. The git diff
2. Stack context (language, framework)
3. Instructions to output findings as structured text with: severity, confidence (1-10), file:line, category, summary, recommended fix

### 4c. Collect and Merge Findings

After all specialists complete:

1. **Deduplicate** — group by file:line:category fingerprint. Multi-specialist confirmation boosts confidence by +1
2. **Apply confidence gates:**

| Score | Meaning | Display Rule |
|-------|---------|-------------|
| 9-10 | Verified by reading specific code. Concrete bug demonstrated. | Show normally |
| 7-8 | High confidence pattern match. Very likely correct. | Show normally |
| 5-6 | Moderate. Could be false positive. | Show with caveat: "Medium confidence — verify" |
| 3-4 | Low confidence. Suspicious but may be fine. | Appendix only |
| 1-2 | Speculation. | Suppress unless severity would be BLOCKER |

3. **Pre-emit verification gate** — before any finding enters the report:
   - **Quote the specific code line** that motivates the finding (file:line + verbatim text)
   - **If you cannot quote the motivating line, the finding is unverified** — force confidence to 4 (appendix only)
   - Never invent confidence 7+ without quoting the code

### 4d. Red Team Review (Conditional)

**Activate if:** diff > 200 lines OR any specialist produced a BLOCKER/CRITICAL finding.

Dispatch one adversarial subagent that receives the merged findings and the diff. Its job is to find what the specialists MISSED:
- Edge cases, race conditions, security holes, resource leaks
- Silent data corruption, logic errors that produce wrong results silently
- Trust boundary violations, error handling that swallows failures
- Thinks like an attacker and a chaos engineer

Red Team findings are tagged `[RED-TEAM]` and merged into the report.

---

## Step 5 — Fix-First Review

**Every finding gets action — not just critical ones.**

### 5a. Classify each finding

For each finding, classify as:
- **AUTO-FIX** — mechanical issues with obvious fixes (missing `await`, unused import, wrong type, simple style issues). Apply these immediately.
- **ASK** — judgment-required issues (architectural decisions, security approach, performance tradeoffs). Present for user decision.

### 5b. Auto-fix all AUTO-FIX items

Apply each fix directly. For each one, output:
`[AUTO-FIXED] [file:line] Problem -> what was done`

### 5c. Batch-ask about ASK items

Present remaining items for user decision:

```
I auto-fixed 5 issues. 2 need your input:

1. [BLOCKER] app/models/user.rb:42 — Race condition in status transition
   Confidence: 9/10
   Fix: Add WHERE status = 'draft' to the UPDATE
   -> A) Fix  B) Skip

2. [MAJOR] app/services/generator.rb:88 — LLM output not type-checked
   Confidence: 7/10
   Fix: Add JSON schema validation
   -> A) Fix  B) Skip

RECOMMENDATION: Fix both — #1 is a real race condition.
```

### 5d. YAGNI Check on Every Suggestion

Before recommending any addition (new abstraction, new validation, new pattern):
- Is this solving a real problem in the current code?
- Or is this a hypothetical future concern?
- If YAGNI, downgrade to SUGGESTION with note: "Only if you expect this pattern to recur"

---

## Step 6 — Write review-report.md

Write to `<working_directory>/review-report.md`:

```markdown
# Code Review Report

> Generated by code-reviewer [date]
> Task reviewed: [S-XXX: story title]
> Files reviewed: [list]
> Review scope: [full / single task / PR / post-fix]
> Specialists dispatched: [list]
> Red Team: [activated / skipped]

## Summary

| Category | Issues Found |
|----------|-------------|
| BLOCKER (must fix before QA) | X |
| MAJOR (should fix before QA) | X |
| MINOR (fix when convenient) | X |
| SUGGESTION (optional improvement) | X |
| AUTO-FIXED | X |
| Total | X |

**Review Verdict**: APPROVED / CHANGES REQUIRED / REJECTED

---

## Scope Drift Check
[Stated intent vs actual changes. Any unplanned additions or missing planned items.]

---

## Plan Completion Audit
[Plan items vs diff. What's done, what's missing.]

---

## Security Checklist
[Table with Requirement | Status | Notes]

---

## Issues

### BLOCKER-001: [Title]
- **Category**: security / architecture / correctness
- **File**: `path/to/file`, line X
- **Confidence**: N/10
- **Specialist**: [core / testing / security / red-team / etc.]
- **Problem**: [what's wrong and WHY it's a problem]
- **Code**: [verbatim quote of the motivating line]
- **Required fix**: [corrected snippet]
- **Reasoning**: [why this matters]

### MAJOR-001: [Title]
...

### AUTO-FIXED-001: [Title]
- **File**: `path/to/file`, line X
- **What was wrong**: [description]
- **Fix applied**: [what was changed]

---

## Acceptance Criteria Check
| Criterion | Implemented | Tested | Notes |

---

## Test Coverage Assessment
| Module | Coverage | Quality | Notes |

---

## Architecture Compliance
| ADR | Compliant | Notes |

---

## Performance Observations
| Issue | Location | Impact | Suggestion |

---

## Carried-Over Findings (from previous reviews)
| Finding | Original Date | Status | Evidence |

---

## Appendix: Low-Confidence Findings (3-4/10)
[Findings below the display threshold — included for transparency]

---

## Files That Need Changes
| File | Changes Needed | Issues |
```

---

## Issue Severity Definitions

| Severity | Definition | Action |
|----------|-----------|--------|
| BLOCKER | Security vulnerability, data loss risk, architectural violation, broken functionality | Must fix before QA. Review again after fix. |
| MAJOR | Missing tests, performance issue, significant code quality problem | Should fix before QA. Minor re-review. |
| MINOR | Naming issues, minor DRY violation, style inconsistency | Fix when convenient. No re-review needed. |
| SUGGESTION | Alternative approach, potential optimization, "nice to have" | Optional. Developer decides. YAGNI check applied. |

---

## Step 7 — Review Loop

1. Write `review-report.md`
2. Present summary with verdict (APPROVED / CHANGES REQUIRED / REJECTED)
3. If CHANGES REQUIRED or REJECTED:
   - Developer fixes issues
   - Re-review ONLY changed files + affected files
   - Verify auto-fixes are still intact
   - Update `review-report.md` with re-review results
   - Repeat until APPROVED
4. Once APPROVED: "Code review passed. Ready for QA — run the `qa-engineer` skill."

**⛔ APPROVED means ZERO open BLOCKER or MAJOR findings.** "APPROVED with recommendations" on a MAJOR is FORBIDDEN — that's how findings die in a drawer and resurface in production. If a MAJOR stands, the verdict is CHANGES REQUIRED, full stop. The only way a MAJOR doesn't block approval is if the user explicitly accepts it in writing, and that acceptance is recorded in the report next to the finding. MINOR and SUGGESTION items may ride along with an approval — MAJORs may not.

---

## Review Principles

- **Be specific** — "line 42 uses SHA256, use bcrypt with cost 12 per ADR-003" not "password hashing is weak"
- **Show the fix** — include corrected code snippets so the developer can copy-paste
- **Explain the why** — "N+1 query will cause 100 DB calls for 100 users" not just "N+1 detected"
- **Don't nitpick** — if it works and follows patterns, don't block on personal style preferences
- **Security is always a blocker** — any security gap from the plan is automatic BLOCKER
- **Praise what's good** — good patterns should be reinforced
- **Review tests as carefully as code** — bad tests are worse than no tests (false confidence)
- **Run it before you judge it** — a review that never built and started the production artifact is a half-review
- **Open findings never expire** — every unresolved MAJOR+ from previous reports carries forward until verified fixed or user-accepted
- **No performative agreement** — when receiving suggestions from others, verify before implementing. Don't agree just to be agreeable.
- **Context matters** — a prototype has different standards than a banking app. Review proportionally.
- **Evidence before claims** — "This looks fine" is not a finding. Cite evidence it IS fine, or flag as unverified.

---

## False Positive Prevention

Known false positive patterns — do NOT flag these:

| Pattern | Why It's Not a Bug |
|---------|-------------------|
| Test fixtures with fake credentials | These are test data, not leaked secrets |
| `process.env.X \|\| "default"` in test configs | Test defaults are safe; only flag in production config |
| SQL in ORM migration files | These are generated/intentional SQL, not injection |
| `any` type in test mocks | Test mocks may legitimately use loose types |
| Console.log in test files | Debug output in tests is fine |
| Hardcoded ports in docker-compose.yml | Container networking, not secrets |
| Example API keys in documentation | Clearly labeled as examples |
