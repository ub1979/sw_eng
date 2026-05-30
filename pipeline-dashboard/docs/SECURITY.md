# Security Overview

This document summarizes the security architecture of the SDLC Pipeline Dashboard, explains the guardrails system, and provides guidance on reporting security issues.

## Threat Model

The SDLC Pipeline Dashboard is a **local-first, single-user** tool. By default it binds to `127.0.0.1:8000` and is not accessible from other machines. The primary security concern is that **LLM-generated commands are executed on your local machine**, so the guardrails engine is the most critical defensive layer.

## Security Architecture

### 1. Guardrails Engine

The guardrails engine (`app/guardrails.py`) provides two layers of defense:

#### Command Allowlist
- Every shell command string is parsed with `shlex.split()`.
- The executable (first token) must appear in `guardrails.json`'s `allowed_executables` list.
- Blocked commands raise `GuardrailsBlocked`, log a security event, and pause the pipeline.
- **No `shell=True` anywhere in the codebase.** All subprocesses use `asyncio.create_subprocess_exec` with explicit argument lists.

#### Path Sandbox
- All file paths are resolved to absolute paths.
- Paths must remain within `projects/<project-id>/`.
- Path traversal patterns (`..`, `/`, `~`) are rejected.
- Symlinks and hard links are not followed outside the sandbox.

### 2. API Security

| Protection | Implementation |
|-----------|----------------|
| SQL Injection | Parameterized queries (`?` placeholders) in all DAO methods (`app/dao.py`) |
| XSS | FastAPI `JSONResponse` auto-escapes; CSP headers block inline scripts from untrusted sources |
| CSRF | `SameSite=Strict` cookies for future auth; state-changing APIs use POST with Pydantic validation |
| Mass Assignment | Pydantic strict models reject extra fields with HTTP 422 |
| CORS | Whitelist only `http://localhost:8000` and `http://127.0.0.1:8000`; never `*` |
| Security Headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin` |
| Request Size | 100KB default for JSON (FastAPI/Starlette default) |

### 3. Database Security

- SQLite file is local filesystem only; no network port exposed.
- WAL mode enabled for ACID compliance.
- Backups written to `data/backups/` with filesystem permissions (`chmod 600` recommended).
- No PII stored in MVP; future multi-user will encrypt sensitive fields.

### 4. Secrets Management

- **Zero secrets in source code.** `.env.example` documents required variables; `.env` is in `.gitignore`.
- Claude/Gemini CLI auth is managed by the CLI binaries themselves (OAuth, config files in `~/.config/`).
- Ollama requires no API key; localhost endpoint is assumed trusted.
- Pre-commit hooks with `gitleaks` or `trufflehog` are recommended to prevent accidental secret commits.

### 5. Network Security

- Binds to `127.0.0.1` by default. Refuse `0.0.0.0` unless behind a reverse proxy with TLS.
- No admin panel in MVP.
- HTTPS not required for localhost; enforce TLS 1.3 if exposed via reverse proxy.

## Guardrails Configuration

### Default Allowlist

The default `guardrails.json` includes safe development tools:

- `python3`, `python`, `node`, `npm`, `npx`, `pip`, `pip3`, `pytest`, `playwright`
- `git`, `docker`, `docker-compose`
- `curl`, `wget`, `cat`, `ls`, `mkdir`, `cp`, `mv`, `rm`, `touch`, `echo`
- `find`, `grep`, `sed`, `awk`, `sort`, `uniq`, `wc`, `tar`, `zip`, `unzip`

### Default Blocklist

Blocked patterns include:

- `sudo`
- `rm -rf /`
- `curl ... | sh` / `curl ... | bash`
- `wget ... | sh`
- Fork bomb (`:(){ :|:& };:`)
- `mkfs`, `dd if=/dev/zero`, `> /dev/sda`
- `chmod 777 /`, `chown -R`

Blocked arguments include `--no-verify`, `--insecure`, `-k`.

### Reloading Guardrails

You can reload `guardrails.json` without restarting the server:

```bash
curl -X POST http://localhost:8000/api/guardrails/reload
```

## Security Testing

The project includes automated security tests:

| Test Type | Tool | Scope |
|-----------|------|-------|
| Dependency CVE Scan | `pip-audit` | `requirements.txt` |
| Python SAST | `bandit` | `app/` directory |
| General Security Audit | `semgrep` | Entire repo (`p/security-audit`) |
| Custom Checks | `scripts/security-scan.sh` | `shell=True`, raw SQL interpolation |
| Guardrails Validation | `tests/unit/test_guardrails.py` | Blocked commands, path traversal |

Run all scans:
```bash
make security-scan
```

## OWASP Risk Assessment

| OWASP Category | Risk Level | Mitigation Status |
|----------------|------------|-------------------|
| A01: Broken Access Control | LOW | Bind to localhost; future JWT + RBAC |
| A02: Cryptographic Failures | LOW | HTTPS for proxy; bcrypt for future passwords |
| A03: Injection | HIGH | Guardrails + parameterized SQL + path sandboxing |
| A04: Insecure Design | MEDIUM | Strict allowlist; user confirmation for overrides |
| A05: Security Misconfiguration | MEDIUM | Restrictive default config; reload requires admin |
| A06: Vulnerable Components | MEDIUM | `pip-audit` before release; Dependabot |
| A07: Auth Failures | LOW | Deferred to post-MVP |
| A08: Data Integrity Failures | LOW | SQLite WAL; immutable completed pipelines |
| A09: Logging Failures | MEDIUM | Structured logs; security events table |
| A10: SSRF | MEDIUM | Ollama URL validated to localhost only |

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not open a public issue.**
2. Email the maintainer with details and reproduction steps.
3. Allow up to 7 days for an initial response and up to 30 days for a fix before public disclosure.

For non-critical security questions (e.g., "Should I allow command X?"), open a discussion in the project repository.
