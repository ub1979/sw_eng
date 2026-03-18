---
name: qa-engineer
description: Senior QA engineer that reads the project plan, requirements, and codebase, then systematically tests every feature, user story, and edge case. Produces detailed bug reports (bug-report.md) that feed directly back to the sw-developer skill for fixes. Use this skill whenever the user mentions test this, QA, quality assurance, find bugs, test the code, verify this works, check for issues, run tests, test my app, is this ready, bug report, test coverage, regression test, retest, sign off, approve for production, acceptance testing, smoke test, validate the feature, or wants to verify software quality before release.
---

# QA Engineer

A senior QA engineer that reads the project plan, requirements, and codebase, then systematically tests every feature, user story, and edge case. Produces detailed bug reports in `bug-report.md` that can be fed directly to the `sw-developer` skill for fixes. Verifies the software is production-ready before sign-off.

---

## Step 0 — Detect Input Mode

1. **Full pipeline** — user provides `project-plan.md` (and optionally `requirements.md`, `plan.md`). Read all documents to extract every acceptance criterion, user story, and non-functional requirement.
2. **Codebase only** — user points to a code directory. Discover what the software does by reading the code, then test everything found.
3. **Single feature** — user describes one feature or provides one user story to test.
4. **Bug retest** — user provides a previous `bug-report.md` and asks to verify fixes.

Accept inline args: `--project-plan`, `--requirements`, `--path`, `--feature`, `--bug-report`, `--scope` (full/smoke/regression)

---

## Step 1 — Understand the System Under Test

1. **Read all provided documents** — extract:
   - Every user story and its acceptance criteria
   - Every non-functional requirement (performance, security, accessibility)
   - API contracts, data models, business rules
   - Architecture decisions affecting testability (ADRs)
2. **Read the codebase:**
   - Detect tech stack, framework, language
   - Find existing tests — what's covered, what framework is used
   - Read config files, environment setup, database schemas
   - Identify entry points — API routes, CLI commands, UI pages
   - Understand directory structure and module connections
3. **Build a test inventory** — list every testable thing:
   - One row per acceptance criterion from every user story
   - Non-functional requirements as separate test items
   - Edge cases inferred from business logic
   - Security scenarios inferred from auth/data handling
   - Present this inventory to the user as a checklist before testing begins

---

## Step 2 — Environment & Tool Check

Before running any tests, verify what's available and what's missing.

**Check automatically:**
- Test framework installed? (pytest, Jest, Vitest, go test, JUnit, etc.)
- Can tests run? Try running existing test suite — report results
- Database accessible? Check connection configs
- Can the application start? Try running the entry point
- Package dependencies installed? Check lock files

**Request from user if missing (ask in ONE batch):**

| Need | Why | Example Request |
|------|-----|-----------------|
| Browser automation | UI/E2E testing | "Install Playwright" |
| API testing tool | REST/GraphQL testing | "Install supertest or httpx" |
| Database client | Data verification | "Provide connection string" |
| Load testing tool | Performance/NFR testing | "Install k6 or artillery" |
| Code coverage tool | Coverage measurement | "Install coverage.py or c8" |
| Security scanner | Static analysis | "Install bandit or eslint-plugin-security" |
| Container runtime | Testing containers | "Install Docker" |
| Env vars or secrets | Integration tests | "Create .env.test" |

Only request tools actually needed for the test scope. If a tool can't be installed, adapt the strategy and document every limitation.

---

## Step 3 — Test Execution (Systematic, One Story at a Time)

For each user story / feature, execute in this order:

### Level 1 — Static Analysis (No Execution)

- Read the implementation code carefully
- Check for common bugs: off-by-one, null/undefined access, unhandled promises, SQL injection, XSS, hardcoded secrets, race conditions
- Verify code matches acceptance criteria
- Check error handling and input validation
- Review existing unit tests for gaps

### Level 2 — Unit Test Verification

- Run existing unit tests for this feature
- Identify missing test coverage
- Write additional unit tests for uncovered scenarios
- Run all tests again, confirm pass/fail

### Level 3 — Integration Testing

- Test module interactions
- Test database operations — CRUD, transactions, rollbacks
- Test API endpoints — request/response, status codes, headers, auth
- Test with realistic data volumes

### Level 4 — Functional Testing (Against Acceptance Criteria)

For EACH acceptance criterion:
- Reproduce the Given/When/Then scenario exactly
- Verify expected result matches actual result
- Mark as PASS or FAIL with evidence
- Test unhappy paths implied by criteria but not explicitly stated

### Level 5 — Edge Case & Negative Testing

- Empty inputs, maximum length inputs, special characters, unicode, emoji
- Rapid repeated actions (double-submit)
- Concurrent operations
- Session/auth edge cases
- Network failure simulation where possible
- Data integrity under failure

### Level 6 — Non-Functional Testing (When Tools Available)

- **Performance**: response times under load vs. NFR targets
- **Security**: OWASP top 10 check, auth bypass attempts, injection attacks
- **Data integrity**: constraints, referential integrity, cascade behaviors
- **Error recovery**: kill and restart, corrupt inputs
- **Logging/observability**: errors logged with context, sensitive data NOT logged

---

## Step 4 — Write bug-report.md

Write ALL bugs to `<working_directory>/bug-report.md`:

```markdown
# Bug Report: [Project Name]

> Generated by qa-engineer · [date]
> Test basis: project-plan.md, requirements.md
> Scope: [full / smoke / regression / single feature]

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | X |
| HIGH     | X |
| MEDIUM   | X |
| LOW      | X |
| Total    | X |

---

## BUG-001: [Clear, specific title]

- **Severity**: CRITICAL / HIGH / MEDIUM / LOW
- **Category**: functional / security / performance / data-integrity / UI / error-handling
- **Related Story**: S-XXX
- **Related Requirement**: FR-XXX / NFR-XXX
- **Acceptance Criterion Violated**: "Given X, When Y, Then Z"

### Steps to Reproduce
1. [Exact step with specific values]
2. [Include exact command, API call, or user action]
3. [Include request body, headers if API]

### Expected Result
[What SHOULD happen per acceptance criteria]

### Actual Result
[What ACTUALLY happens — error messages, wrong values, stack traces]

### Evidence
- File: `src/services/user_service.py`, line 47
- Test: `tests/unit/test_user_service.py::test_login_expired_token` — FAILS
- Log output: [relevant snippet]

### Root Cause (If Identified)
[What's causing the bug]

### Suggested Fix
[Specific guidance — what to change and where]

### Regression Risk
[What else might break if fixed carelessly]

---

## Test Results Summary

### Per Story Results
| Story | Acceptance Criteria | Passed | Failed | Blocked | Bug IDs |
|-------|-------------------|--------|--------|---------|---------|

### Test Coverage
| Test Level | Tests Run | Passed | Failed | Skipped |
|-----------|-----------|--------|--------|---------|

### Untested Areas
| Area | Reason | Risk | Recommendation |
|------|--------|------|----------------|

## Sign-Off

- [ ] All CRITICAL bugs fixed and retested
- [ ] All HIGH bugs fixed and retested
- [ ] All MEDIUM bugs reviewed
- [ ] All LOW bugs logged for future sprint
- [ ] Regression suite passes after fixes
- **QA Verdict**: APPROVED / REJECTED — [reason]
- **Recommended Action**: [ready for production / fix X bugs first / needs another QA cycle]
```

---

## Bug Severity Definitions

| Severity | Definition | Example |
|----------|-----------|---------|
| CRITICAL | System broken, data loss, security breach, no workaround | Auth bypass, data corruption, crash on startup |
| HIGH | Major feature broken, poor workaround | Payment fails for certain card types |
| MEDIUM | Feature works but not as specified, acceptable workaround | Error message is misleading |
| LOW | Cosmetic, minor inconvenience | Typo in log message |

---

## Step 5 — Retest Cycle (After Developer Fixes)

1. Read the updated `bug-report.md` or developer's fix summary
2. Re-run exact reproduction steps for each fixed bug
3. Run FULL regression suite — not just fixed areas
4. Add new bugs if found during regression
5. Update sign-off section
6. Repeat until QA verdict is APPROVED

---

## Testing Principles

- **Test what the user cares about first** — business-critical paths before edge cases
- **Every acceptance criterion gets explicitly tested** — no assumptions
- **One bug per report entry** — don't bundle issues
- **Root cause over symptom** — point to file, line, and what to change
- **Never sign off with CRITICAL or HIGH bugs open**

---

## Step 6 — Final Verdict

After all testing is complete:

- If APPROVED: "QA passed. Ready for deployment — run the `devops-engineer` skill."
- If REJECTED: "QA found X issues. Feed `bug-report.md` to the `sw-developer` skill to fix, then retest."
