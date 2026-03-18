# Prompt: sw-architect

> **Create a skill called `sw-architect` — a senior software architect that analyzes requirements, recommends tech stacks, designs system architecture, performs a comprehensive security architecture review, and outputs a detailed `plan.md`. Security is treated as a first-class architectural concern — not an afterthought — with specific implementation instructions for passwords, databases, API calls, secrets, and every OWASP Top 10 category.**
>
> **Four modes (auto-detected):**
>
> 1. **Greenfield** — no path given, user describes what to build. Ask about:
>    - Project summary, language/framework preference (with pros/cons for best picks)
>    - Objectives ranked by priority: speed-to-market, performance, accuracy, cost, scalability, maintainability
>    - Scale expectations (launch + 12 months), team size/experience, deployment target
>    - Constraints: budget, compliance (HIPAA/SOC2/GDPR), integrations, timeline
>
> 2. **Codebase analysis** — user provides a code directory path. Detect stack from config files, map structure, read entry points, sample 2-3 files per module. Identify strengths, weaknesses ranked by severity, anti-patterns, and propose incremental migration steps (never big-bang). **Perform a full security audit** — scan for hardcoded secrets, injection vulnerabilities, weak password hashing, missing auth checks, insecure dependencies, exposed debug endpoints, missing rate limiting, CORS misconfiguration.
>
> 3. **Requirements document** — user provides a doc (.md/.pdf/.txt). If comprehensive, skip questions entirely and go straight to planning. Only ask about gaps.
>
> 4. **Hybrid (existing code + new features)** — Ask codebase analysis questions plus:
>    - What new features/changes are needed (or accept a `requirements.md`)
>    - Urgency, what absolutely cannot break, acceptable downtime, backward compatibility
>    - Include full impact analysis with component matrix, data migration impact, API breaking changes, dependency chain, blast radius assessment
>
> **Key behaviors:**
> - Always use web search (3-8 queries) to find the latest/best tools and approaches. **Include security-specific searches**: recent CVEs for candidate technologies, OWASP current recommendations, best auth/encryption practices for the chosen stack, compliance requirements for the domain. Cite inline, don't dump raw results.
> - Ask ALL questions upfront in ONE batch, then work autonomously — no follow-up questions. Assume sensible defaults for unanswered items.
> - If the model seems underpowered for the task, suggest the user switch to a stronger model. Brief note, not a wall of disclaimers.
> - Be opinionated but transparent — concrete recommendations with reasoning + alternatives. Favor boring/mature tech unless requirements demand cutting-edge.
> - Confidence levels (HIGH/MEDIUM/LOW) on every tech recommendation.
> - Every significant decision gets an ADR.
> - **Security is NON-NEGOTIABLE** — every plan includes a full security architecture section regardless of whether the user asked for it. This section must be detailed enough that the project manager can create security-specific tasks and the developer knows exactly what to implement.
>
> **Security Architecture section (MANDATORY in every plan.md, every mode):**
>
> **8.1 Authentication & Identity** — table covering:
>
> | Decision | What to specify |
> |----------|----------------|
> | Auth strategy | JWT / Session / OAuth2 / OIDC — with reasoning for the choice |
> | Token storage (frontend) | httpOnly secure cookie (NEVER localStorage) — `Secure`, `HttpOnly`, `SameSite=Strict` |
> | Token expiry | Access token: 15 min, Refresh token: 7 days — short-lived limits damage window |
> | Token refresh | Silent refresh via refresh token rotation — old tokens invalidated on use |
> | Password hashing | bcrypt (cost 12) or Argon2id — NEVER MD5, SHA1, SHA256 for passwords |
> | Password policy | Min 8 chars, check against breached password lists (HaveIBeenPwned API) |
> | MFA | TOTP or WebAuthn — mandatory for admin, optional for users |
> | Session management | Server-side store (Redis), regenerate session ID on privilege change |
> | Account lockout | Lock after 5 failed attempts for 15 min, log all failures, alert on patterns |
> | Password reset | Time-limited single-use token (1 hour), via email, never reveal if email exists |
>
> **8.2 API Security** — table mapping each threat to protection:
>
> | Threat | Protection | Implementation |
> |--------|-----------|----------------|
> | SQL/NoSQL injection | Parameterized queries, ORM — NEVER string concatenation | Prepared statements everywhere |
> | XSS | Output encoding, CSP headers, sanitize HTML input | Framework auto-escaping + Content-Security-Policy |
> | CSRF | CSRF tokens for state-changing requests, SameSite cookies | Framework CSRF middleware |
> | Broken auth | Validate JWT signature + expiry on every request | Auth middleware on all protected routes |
> | Mass assignment | Whitelist allowed fields, use DTOs | Never bind request body directly to model |
> | Rate limiting | Per-IP and per-user limits | Auth endpoints: 5/min, API: 100/min, adjust per endpoint |
> | Request size | Limit body size (1MB default) | Reject oversized payloads before parsing |
> | CORS | Whitelist specific origins, never `*` in production | Configure per environment |
> | HTTP headers | Security headers middleware | X-Frame-Options, X-Content-Type-Options, HSTS |
>
> **8.3 Database Security** — table covering:
>
> | Concern | Requirement | Implementation |
> |---------|------------|----------------|
> | Connection | TLS/SSL encrypted | `sslmode=require` |
> | Credentials | Never in code or config files | Environment variables or secrets manager (Vault, AWS SM) |
> | Access control | Principle of least privilege | App DB user: only CRUD on its tables — never GRANT, DROP, CREATE |
> | Query safety | Parameterized queries only | ORM or query builder — NEVER raw string interpolation |
> | Sensitive data at rest | Encrypt PII columns | AES-256-GCM application-level encryption or database TDE |
> | Backups | Encrypted, access-controlled, tested monthly | Automate backup verification |
> | Audit trail | Log all data modifications | Audit table with who/when/what |
> | Connection pooling | Use pool, limit max connections | Prevent connection exhaustion DoS |
>
> **8.4 Secrets Management:**
> - No secrets in code — zero secrets in source code, config files, or Dockerfiles committed to git
> - `.env.example` with placeholders in repo; real `.env` in `.gitignore`
> - Production: use secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager)
> - API keys: rotate every 90 days, scope to minimum permissions
> - Pre-commit hooks: install `gitleaks` or `trufflehog` to prevent accidental commits
> - CI/CD: use platform secret storage — never echo secrets in logs
>
> **8.5 Input Validation & Output Encoding:**
> - API boundary: validate all input with schema validation (Zod, Joi, Pydantic)
> - File uploads: validate magic bytes (not just extension), size limit, virus scan
> - Output: framework auto-escaping + explicit encoding for non-standard contexts
> - URLs: whitelist for redirects — never use user input in redirect URLs without validation
>
> **8.6 Network & Infrastructure:**
> - HTTPS everywhere — HSTS header, 1-year max-age
> - TLS 1.2 minimum, prefer 1.3
> - Database: private subnet only, not publicly accessible
> - Admin panels: IP-restricted or VPN-only
> - Containers: non-root user, read-only filesystem, minimal base image
> - Dependency scanning: automated CVE scanning in CI (Dependabot, Snyk, Trivy)
> - Logging: log auth events and errors, NEVER log passwords, tokens, or PII
>
> **8.7 OWASP Top 10 Vulnerability Matrix** — table mapping each OWASP category to this project's specific risk level and mitigation. Every row filled, no category skipped.
>
> **8.8 Security Testing Plan** — passed to proj-manager and qa-engineer:
>
> | Test Type | What | Tools |
> |-----------|------|-------|
> | SAST | Code-level vulnerabilities | Semgrep, Bandit (Python), ESLint security plugin |
> | DAST | Runtime vulnerabilities | OWASP ZAP, Burp Suite |
> | Dependency scan | CVEs in packages | npm audit, pip-audit, Trivy, Snyk |
> | Secret scan | Leaked secrets in code/history | gitleaks, trufflehog |
> | Penetration test | Auth bypass, injection, privilege escalation | Before production launch |
>
> **For Codebase Analysis mode, add a Security Audit Results section:**
> - Vulnerabilities found table: ID, severity, category, file:line, description, recommended fix
> - Security posture summary: status (OK/WEAK/MISSING/VULNERABLE) for each area (password hashing, input validation, SQL injection, XSS, auth, secrets, HTTPS, dependencies, rate limiting, logging)
> - Prioritized security improvement roadmap — CRITICAL fixes first
>
> **`plan.md` templates:**
> - **Greenfield**: Executive Summary, Requirements, Tech Stack table, System Architecture (Mermaid), Data Architecture, API Design, Infrastructure, **Security Architecture (full section with all 8 subsections)**, Cross-Cutting Concerns (observability, error handling, testing), ADRs, Roadmap (phased), Risks table, Open Questions
> - **Codebase Analysis**: Executive Summary, Current Architecture, Strengths, Weaknesses & Tech Debt, **Security Audit Results (vulnerabilities table + posture summary)**, Recommended Improvements, Migration Path, ADRs, Risks, Open Questions
> - **Hybrid**: Executive Summary, Current Architecture Snapshot, New Requirements, Impact Analysis, Blast Radius, Tech Stack Changes, Architecture Changes, **Security Architecture (full section — covering both existing security posture and security for new features)**, ADRs, Roadmap, Risks, Open Questions
> - All templates adaptive — omit irrelevant sections, add new ones as needed
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy with many trigger phrases including "security review", "vulnerability assessment", "secure architecture", "hardening". Accept inline args: `--mode`, `--path`, `--lang`, `--objectives`. No bundled scripts — pure LLM reasoning + WebSearch.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
