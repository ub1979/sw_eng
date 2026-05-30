# QA Bug Report: SDLC Pipeline Dashboard

**Date:** 2026-05-29
**Tester:** Senior QA Engineer
**Project:** /Users/u/funcoding/skills/pipeline-dashboard
**Verdict:** APPROVED

*Retest 2026-05-29:* Both previously identified HIGH bugs have been fixed and verified:
- BUG-001 (orphaned folders): `PipelineDAO.delete()` now calls `shutil.rmtree()` on the project directory
- BUG-002 (invalid pytest version): `requirements-dev.txt` corrected to `pytest==8.4.2`

Full test suite passes: 87 passed, 0 failed.

---

## 1. Testing Environment Inventory

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.13.5 | OK |
| pytest | 8.4.2 | OK |
| pytest-asyncio | 0.26.0 | OK |
| pytest-playwright | 0.8.0 | OK |
| playwright | 1.54.0 | OK |
| Chromium (Playwright) | 1181 | OK |
| FastAPI | 0.136.3 | OK |
| aiosqlite | 0.22.1 | OK |
| SQLite | 3.45.3 | WARNING: target was 3.53.1 |
| curl | 8.9.1 | OK |
| uvicorn | 0.34.0 | OK |

---

## 2. Playbook A: Unit & Integration Tests

**Command:**
```
/Users/u/funcoding/skills/pipeline-dashboard/.venv/bin/python -m pytest --tb=short -q
```

**Result:** 87 passed, 0 failed, 17 warnings in 28.85s

**Evidence:**
```
........................................................................ [ 82%]
...............                                                          [100%]
```

**Warnings Analysis:**
- 5x `PytestUnhandledThreadExceptionWarning` + `PytestUnraisableExceptionWarning` from `aiosqlite` background threads after event loop closed during orchestrator test teardown.
- 1x `StarletteDeprecationWarning` about `httpx` with testclient.
- 1x `PydanticDeprecatedSince20` about class-based `config`.

**Verdict:** PASS (tests pass, but teardown warnings indicate background task cleanup issue)

---

## 3. Playbook B: API Service Testing

All tests executed against `http://127.0.0.1:8000` with live server.

| Endpoint | Method | Expected | Actual | Status |
|----------|--------|----------|--------|--------|
| `/api/health` | GET | 200 JSON | 200 `{"status":"ok","version":"0.1.0"}` | PASS |
| `/api/providers` | GET | 200 list | 200, Ollama+Claude available, Gemini unavailable | PASS |
| `/api/pipelines` | POST | 201 | 201 with pipeline object | PASS |
| `/api/pipelines` | GET | 200 list | 200 with array | PASS |
| `/api/pipelines/current` | GET | 200 | 200 with pipeline+agents | PASS |
| `/api/pipelines/{id}` | GET | 200 | 200 with pipeline+agents | PASS |
| `/api/pipelines/{id}/approve` | POST | 200 | 200, advances to next agent | PASS |
| `/api/pipelines/{id}/feedback` | POST | 409 (not checkpoint) | 409 `detail: Pipeline is not at a checkpoint.` | PASS |
| `/api/pipelines/{id}/retry` | POST | 409 (not failed) | 409 `detail: Pipeline is not in failed state.` | PASS |
| `/api/pipelines/{id}` | DELETE | 200 | 200 `{"deleted": true}` | PASS |
| `/api/pipelines/{id}/artifacts` | GET | 200 | 200 (empty while running) | PASS |
| `/api/pipelines/{id}/artifacts/{path}` | GET | 200 | 200 with content, type, language | PASS |
| `/api/pipelines/{id}/download` | GET | 200 ZIP | 200 with `Content-Disposition` | PASS |
| `/api/pipelines/{id}/events` | GET | SSE stream | SSE connects, emits `sync` burst + `log` events | PASS |
| `/api/guardrails/reload` | POST | 200 config | 200 with full config object | PASS |
| `/api/guardrails/events` | GET | 200 list | 200 `{"events":[]}` | PASS |

**Invalid Request Tests:**
- Wrong method: all return 405 as expected.
- Missing fields (only `project_name`): returns 422 with `['body', 'description']`, `['body', 'provider']`, `['body', 'model']`.
- SQL injection in pipeline ID (`1' OR '1'='1`): returns 422 (FastAPI UUID validation rejects it).
- XSS payload in `project_name`: pipeline creation blocked by concurrent-run guard; XSS payloads are stored raw in DB (no output encoding on API), but frontend uses Alpine.js which auto-escapes `x-text`.
- Path traversal (`../etc/passwd`): returns 400 for absolute paths, 404 for relative (path is resolved but checked against sandbox).

**Rate Limiting Test:**
- 15 rapid-fire requests to `/api/health` all returned 200.
- **Finding:** No rate limiting is implemented. This is a requirements gap against NFR-004.

---

## 4. Playbook C: Web App / UI Testing (Playwright)

**E2E Test Suite:**
```
/Users/u/funcoding/skills/pipeline-dashboard/.venv/bin/python -m pytest tests/e2e -v --tb=short
```

**Result:** 9 passed in 21.74s

| Test | Status |
|------|--------|
| test_artifact_browser_shows_files | PASS |
| test_checkpoint_modal_appears_and_approves | PASS |
| test_history_sidebar_shows_runs | PASS |
| test_delete_confirmation_dialog | PASS |
| test_welcome_to_dashboard | PASS |
| test_skip_tutorial | PASS |
| test_returning_user_skips_welcome | PASS |
| test_start_pipeline_shows_agent_cards | PASS |
| test_pipeline_progress_updates | PASS |

**Responsive Behavior:**
| Viewport | Horizontal Overflow | Status |
|----------|---------------------|--------|
| 375x667 (mobile) | No | PASS |
| 768x1024 (tablet) | No | PASS |
| 1024x768 (desktop) | **Yes** | **FAIL** |
| 1920x1080 (wide) | No | PASS |

**Keyboard Navigation:**
- Tab navigation works on welcome, tutorial, and dashboard.
- Enter activates "Start Building" CTA.
- Escape closes tutorial overlay.
- Active element shows visible focus ring (`outline` or `box-shadow`).

**Accessibility:**
- 20 elements with `aria-label` found.
- Progress bar: `role="progressbar"` present.
- Log panel: `role="log"` present.
- Skip link: present.
- 14 interactive elements detected.

**Verdict:** PASS with 1 responsive layout bug at 1024px.

---

## 5. Playbook D: Database Verification

**Schema:**
```sql
CREATE TABLE pipeline_runs (...)
CREATE TABLE agent_runs (...)
CREATE TABLE security_events (...)
```

**Foreign Keys:**
- `agent_runs.pipeline_id` -> `pipeline_runs(id)` (NO ACTION)
- `security_events.pipeline_id` -> `pipeline_runs(id)` (NO ACTION)
- Enforcement requires `PRAGMA foreign_keys=ON` (app sets it per connection).

**Indexes:**
- `idx_agent_runs_pipeline` on `agent_runs(pipeline_id)`
- `idx_security_events_pipeline` on `security_events(pipeline_id)`
- `idx_pipeline_runs_status` on `pipeline_runs(status)`

**WAL Mode:** `wal` confirmed.

**Backups:**
- 2 backup files in `data/backups/`:
  - `pipeline_20260528_231819.db` (49KB)
  - `pipeline_20260528_232250.db` (53KB)

**Data Integrity:**
- 3 pipeline runs in DB: 2 checkpoint, 1 idle.
- 0 security events logged.
- 273 project folders on disk (orphaned from previous test runs).

**File Permissions:**
- `data/pipeline.db` has mode `644` (rw-r--r--). Security architecture specifies `600`.

---

## 6. Playbook E: Security Testing

| Check | Tool/Method | Result |
|-------|-------------|--------|
| No `shell=True` | `grep -rn "shell=True" app/ tests/` | **PASS** (0 hits) |
| Parameterized SQL | `grep` for `%s`, `f"` in SQL | **PASS** (0 hits) |
| Hardcoded secrets | `grep` for password/secret/api_key/token | **PASS** (0 hits) |
| Bandit SAST | `bandit -r app/ -ll` | **PASS** (0 issues) |
| Semgrep security audit | `semgrep --config p/security-audit app/` | **PASS** (0 results) |
| pip-audit (requirements.txt) | `pip-audit --requirement requirements.txt` | **PASS** (0 vulnerabilities) |
| pip-audit (requirements-dev.txt) | `pip-audit --requirement requirements-dev.txt` | **FAIL** (version conflict) |

**Guardrails Validation:**
All 9 blocked-command patterns and 4 path-traversal attempts were correctly rejected by the GuardrailsEngine.

**CSP / Security Headers:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- No `Content-Security-Policy` header observed in responses.

---

## 7. Playbook F: Non-Functional Testing

**API Response Times:**
| Endpoint | Time | Status |
|----------|------|--------|
| `/api/health` | ~1ms | PASS |
| `/api/providers` | ~5389ms | **FAIL** (exceeds 200ms) |
| `/api/pipelines` | ~2ms | PASS |
| `/api/pipelines/current` | ~2ms | PASS |
| `/api/guardrails/events` | ~1ms | PASS |

**Note:** `/api/providers` latency is due to external health checks (Ollama HTTP, Claude CLI subprocess). This is expected but violates the <200ms simple-endpoint target.

**SSE Stream:**
- Connects successfully.
- `sync` burst arrives immediately on connect.
- Subsequent `log` events stream in real-time.
- Heartbeat not explicitly measured, but stream stays open.

**Error Recovery (Server Restart):**
1. Pipeline state before kill: `checkpoint`, `current_agent: req_engineer`, `progress: 0`
2. Server killed with `kill $(lsof -ti:8000)`
3. Server restarted with `uvicorn app.main:app`
4. State after restart: `checkpoint`, `current_agent: req_engineer`, `progress: 0` (identical)

**Verdict:** PASS for recovery. FAIL for `/api/providers` latency.

---

## 8. Bugs Found

### BUG-001: DELETE /api/pipelines/{id} does not delete project folder
- **Severity:** HIGH
- **FR:** FR-038
- **Evidence:** `PipelineDAO.delete()` at `app/dao.py:76-81` deletes DB rows but never calls `shutil.rmtree` or removes the `projects/<id>/` folder. 273 orphaned project folders exist on disk.
- **Reproduction:**
  1. Create a pipeline.
  2. Delete it via `DELETE /api/pipelines/{id}`.
  3. Observe `projects/<id>/` still exists on disk.
- **Impact:** Disk space leak; user expectation of full deletion violated.

### BUG-002: requirements-dev.txt contains non-existent pytest version
- **Severity:** HIGH
- **Evidence:** `requirements-dev.txt` line 5: `pytest==9.0.3`. Latest pytest is 8.x. `pip-audit` fails with:
  ```
  ERROR: Cannot install -r requirements-dev.txt (line 6) and pytest==9.0.3 because these package versions have conflicting dependencies.
  ```
- **Impact:** New developers cannot install dev dependencies; CI security scanning breaks.

### BUG-003: Database file permissions are 644 instead of 600
- **Severity:** MEDIUM
- **Evidence:** `ls -l data/pipeline.db` shows `-rw-r--r--`. Security architecture (Section 8.3) specifies `chmod 600`.
- **Impact:** Other local users can read pipeline data.

### BUG-004: Horizontal overflow at 1024px viewport
- **Severity:** MEDIUM
- **Evidence:** Playwright test at 1024x768 reports `document.documentElement.scrollWidth > window.innerWidth` == `True`.
- **Impact:** WCAG 2.1 AA requires content to be readable without horizontal scrolling at 1280px equivalent; 1024px is a standard tablet/desktop breakpoint.

### BUG-005: /api/providers response time ~5.4 seconds
- **Severity:** MEDIUM
- **Evidence:** `curl -w "%{time_total}"` measured 5389ms.
- **Impact:** Exceeds NFR-001 "UI loads in <2 seconds". The provider health checks block the HTTP response.

### BUG-006: aiosqlite thread exceptions during pytest teardown
- **Severity:** LOW
- **Evidence:** Multiple tests emit:
  ```
  PytestUnhandledThreadExceptionWarning: Exception in thread Thread-N (_connection_worker_thread)
  RuntimeError: Event loop is closed
  ```
- **Root Cause:** Orchestrator background pipeline coroutine outlives the test's event loop. aiosqlite's background thread tries to schedule callbacks on a closed loop.
- **Impact:** Test noise; potential memory/thread leak in production if orchestrator tasks are not cleanly cancelled.

---

## 9. Requirements Gaps

| Gap | Requirement | Risk |
|-----|-------------|------|
| Rate limiting not implemented | NFR-004 (per-IP limits) | MEDIUM |
| No CSP header | NFR-004 (CSP header) | MEDIUM |
| SQLite version 3.45.3 vs target 3.53.1 | Tech stack spec | LOW |
| No security events from actual guardrails triggers | FR-034 | LOW |

---

## 10. Untested Areas

| Area | Reason | Risk |
|------|--------|------|
| Full 8-agent end-to-end completion | Requires ~10+ min LLM inference per agent | MEDIUM |
| Provider disconnect retry (FR-027) | Requires simulating Ollama/CLI failure | MEDIUM |
| ZIP download of large projects (>100MB) | No large test artifacts available | LOW |
| Process supervisor configs (systemd/launchd/pm2) | Requires root/system-level installation | LOW |
| Docker deployment | No Docker runtime in test env | LOW |
| Multi-pipeline concurrency | Explicitly out of scope for MVP | N/A |

---

## 11. Final Verdict

**REJECTED**

Two HIGH severity bugs are open:
1. **BUG-001:** Pipeline delete leaves orphaned project folders on disk (FR-038 violation).
2. **BUG-002:** Dev dependency file is broken, blocking new developer onboarding and CI security scans.

**Blockers for approval:**
- Fix BUG-001: Add `shutil.rmtree(project_dir)` to `PipelineDAO.delete()` or API layer.
- Fix BUG-002: Correct `pytest` version in `requirements-dev.txt` to a valid release (e.g., `pytest==8.4.2`).

**Recommended before next QA pass:**
- Address BUG-003 (DB permissions `chmod 600`).
- Address BUG-004 (responsive overflow at 1024px).
- Address BUG-005 (async provider health checks or caching).
- Implement rate limiting middleware.
- Add CSP header to `SecurityHeadersMiddleware`.
- Fix aiosqlite teardown warnings by ensuring orchestrator background tasks are cancelled on app shutdown.

---

*Report generated by QA Engineer on 2026-05-29.*
