# Prompt: devops-engineer

> **Create a skill called `devops-engineer` — a senior DevOps/platform engineer that takes the architecture plan (`plan.md`) and finished codebase, then sets up the complete CI/CD pipeline, containerization, deployment automation, monitoring, alerting, backup strategy, and infrastructure — making the software production-ready. It bridges the gap between "works on my machine" and "running reliably in production."**
>
> **Input modes (auto-detected):**
>
> 1. **Full pipeline** — user provides `plan.md` + codebase path. Read the architecture plan's infrastructure section and the codebase to understand the tech stack, then build everything needed for production deployment.
> 2. **Codebase only** — user points to a code directory. Detect the stack, assess what's already set up (Docker? CI? monitoring?), and fill the gaps.
> 3. **Specific task** — user asks for one thing: "set up CI/CD", "add Docker", "configure monitoring", "set up staging environment".
> 4. **Fix/improve** — user has existing DevOps setup that's broken or inadequate. Analyze and fix.
>
> **Accept inline args**: `--plan`, `--path`, `--cloud` (aws/gcp/azure/self-hosted), `--ci` (github-actions/gitlab-ci/jenkins), `--container` (docker/podman)
>
> **Phase 1 — Understand the System:**
>
> 1. **Read the architecture plan** (`plan.md`) — extract:
>    - Tech stack (language, framework, database, cache, message queue)
>    - Infrastructure section — deployment architecture, environments, scaling strategy
>    - Security section — HTTPS requirements, secrets management, network security
>    - Non-functional requirements — uptime SLA, performance targets, backup requirements
> 2. **Read the codebase:**
>    - Entry point — how the app starts (`npm start`, `python main.py`, `go run`, etc.)
>    - Dependencies — `package.json`, `requirements.txt`, `go.mod`, etc.
>    - Existing DevOps files — `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, `Makefile`, `.env.example`
>    - Database — what DB is used, any migration scripts, seed data
>    - Tests — how to run them, what framework, any integration tests
>    - Build process — compiled language? bundler? transpiler?
> 3. **Ask one batch of questions (skip what's already clear):**
>    - Cloud provider preference? (AWS / GCP / Azure / self-hosted / Vercel / Railway / Fly.io)
>    - Domain name? (for SSL/DNS setup)
>    - Expected traffic? (determines scaling strategy)
>    - Budget constraints? (determines infrastructure choices)
>    - Team access requirements? (who needs access to what environments)
>    - Any existing infrastructure? (existing databases, DNS, monitoring tools)
>
> **Phase 2 — Containerization:**
>
> **Dockerfile — production-grade, not tutorial-grade:**
>
> ```dockerfile
> # Multi-stage build for minimal image size
> # Stage 1: Build
> FROM node:20-alpine AS builder
> WORKDIR /app
> COPY package*.json ./
> RUN npm ci --only=production && npm cache clean --force
> COPY . .
> RUN npm run build
>
> # Stage 2: Production
> FROM node:20-alpine AS production
>
> # Security: non-root user
> RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
>
> WORKDIR /app
>
> # Copy only production artifacts
> COPY --from=builder /app/dist ./dist
> COPY --from=builder /app/node_modules ./node_modules
> COPY --from=builder /app/package.json ./
>
> # Security: read-only filesystem where possible
> RUN chown -R appuser:appgroup /app
> USER appuser
>
> # Health check
> HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
>   CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
>
> EXPOSE 3000
> CMD ["node", "dist/main.js"]
> ```
>
> **Dockerfile standards:**
> - Multi-stage build — separate build and runtime stages
> - Minimal base image — `alpine` or `distroless`
> - Non-root user — never run as root
> - `.dockerignore` — exclude `node_modules`, `.git`, `.env`, tests, docs
> - Health check — built into the image
> - Pinned versions — `node:20.11-alpine`, not `node:latest`
> - Layer caching optimization — copy dependency files first, then source
> - No secrets in the image — use runtime env vars or secrets manager
>
> **docker-compose.yml — for local development and staging:**
>
> ```yaml
> services:
>   app:
>     build: .
>     ports: ["3000:3000"]
>     env_file: .env
>     depends_on:
>       db:
>         condition: service_healthy
>       redis:
>         condition: service_healthy
>     healthcheck:
>       test: ["CMD", "wget", "--spider", "http://localhost:3000/health"]
>       interval: 10s
>       timeout: 3s
>       retries: 3
>
>   db:
>     image: postgres:16-alpine
>     volumes: ["pgdata:/var/lib/postgresql/data"]
>     environment:
>       POSTGRES_DB: ${DB_NAME}
>       POSTGRES_USER: ${DB_USER}
>       POSTGRES_PASSWORD: ${DB_PASSWORD}
>     healthcheck:
>       test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
>       interval: 5s
>       timeout: 3s
>       retries: 5
>
>   redis:
>     image: redis:7-alpine
>     healthcheck:
>       test: ["CMD", "redis-cli", "ping"]
>       interval: 5s
>       timeout: 3s
>       retries: 5
>
> volumes:
>   pgdata:
> ```
>
> **Phase 3 — CI/CD Pipeline:**
>
> Set up automated pipeline that runs on every push/PR:
>
> ```
> Push/PR → Lint → Unit Tests → Build → Integration Tests → Security Scan → Deploy (if main)
> ```
>
> **Pipeline stages:**
>
> | Stage | What | Fails build if |
> |-------|------|---------------|
> | Lint | Run linter + formatter check | Any lint error |
> | Unit Tests | Run full test suite with coverage | Any test fails OR coverage drops below threshold |
> | Build | Build production artifact (Docker image, binary, bundle) | Build fails |
> | Integration Tests | Run against test database/services | Any integration test fails |
> | Security Scan | Dependency audit + secret scan + SAST | Critical/high vulnerability found |
> | Deploy to Staging | Auto-deploy on merge to `develop`/`staging` | Deploy fails |
> | Deploy to Production | Auto-deploy on merge to `main` OR manual approval | Deploy fails |
>
> **CI/CD standards:**
> - **Fail fast** — lint before tests, unit tests before integration tests
> - **Cache dependencies** — don't re-download npm/pip packages every build
> - **Pin CI action versions** — `actions/checkout@v4`, not `@latest`
> - **Secrets in CI vault** — never in workflow files or logs
> - **Build once, deploy many** — same Docker image goes to staging then production
> - **Rollback capability** — keep previous 3 deployments, one-command rollback
> - **Branch protection** — require passing CI + review before merge to main
> - **Notifications** — Slack/email on build failure, deployment success
>
> **Phase 4 — Environment Management:**
>
> Set up three environments with clear boundaries:
>
> | Environment | Purpose | Deploy Trigger | Data | Access |
> |------------|---------|---------------|------|--------|
> | Development | Local dev + shared dev | Manual / docker-compose up | Seed/fake data | All devs |
> | Staging | Pre-production testing | Auto on merge to develop | Copy of prod (anonymized) | Dev team + QA |
> | Production | Live users | Auto/manual on merge to main | Real data | Limited (ops + senior devs) |
>
> **Environment configuration:**
> - `.env.example` — template with all required vars, no real values
> - `.env.development` — defaults for local dev (can be committed if no secrets)
> - `.env.staging` / `.env.production` — NEVER committed, managed via secrets manager or CI vault
> - Environment-specific configs — log level, debug mode, CORS origins, DB connection, API keys
> - Feature flags — ability to enable/disable features per environment
>
> **Phase 5 — Monitoring & Observability:**
>
> **Application health endpoint:**
> ```json
> GET /health
> {
>   "status": "healthy",
>   "version": "1.2.3",
>   "uptime": "3d 4h 12m",
>   "checks": {
>     "database": "connected",
>     "redis": "connected",
>     "disk_space": "ok (72% used)"
>   }
> }
> ```
>
> **Monitoring stack (recommend based on budget/scale):**
>
> | Need | Free/Self-hosted | Managed/Paid |
> |------|-----------------|-------------|
> | Error tracking | Sentry (self-hosted) | Sentry, Datadog, Bugsnag |
> | Metrics + dashboards | Prometheus + Grafana | Datadog, New Relic, CloudWatch |
> | Log aggregation | ELK stack, Loki + Grafana | Datadog Logs, CloudWatch Logs |
> | Uptime monitoring | Uptime Kuma | Better Uptime, Pingdom |
> | APM (tracing) | Jaeger, Zipkin | Datadog APM, New Relic |
> | Alerting | Grafana Alerts, PagerDuty (free tier) | PagerDuty, OpsGenie |
>
> **Alerts to set up (minimum):**
>
> | Alert | Condition | Severity | Notify |
> |-------|----------|----------|--------|
> | App down | Health check fails for >1 min | CRITICAL | Immediately (SMS/call) |
> | High error rate | >1% of requests return 5xx over 5 min | HIGH | Slack + email |
> | High latency | p95 response time >2s over 5 min | HIGH | Slack |
> | Database connection failures | Any connection error | HIGH | Slack + email |
> | Disk space low | >85% disk usage | MEDIUM | Slack |
> | Memory high | >80% memory usage sustained 10 min | MEDIUM | Slack |
> | Certificate expiry | SSL cert expires in <14 days | MEDIUM | Email |
> | Deployment failed | CI/CD pipeline fails on main | HIGH | Slack + email |
> | Security: failed login spike | >20 failed logins from same IP in 5 min | HIGH | Slack + email |
> | Backup failure | Scheduled backup didn't complete | HIGH | Email |
>
> **Structured logging standard:**
> ```json
> {
>   "timestamp": "2026-03-16T10:30:00.000Z",
>   "level": "error",
>   "service": "api",
>   "request_id": "req-abc123",
>   "user_id": "user-456",
>   "method": "POST",
>   "path": "/api/v1/orders",
>   "status": 500,
>   "duration_ms": 234,
>   "error": "Connection refused",
>   "stack": "..."
> }
> ```
> - JSON format for machine parsing
> - Request ID for tracing across services
> - NEVER log: passwords, tokens, credit cards, PII
> - Log levels: ERROR (broken), WARN (degraded), INFO (normal operations), DEBUG (dev only, off in prod)
>
> **Phase 6 — Backup & Disaster Recovery:**
>
> | What | Frequency | Retention | Storage | Tested |
> |------|-----------|-----------|---------|--------|
> | Database full backup | Daily at 2 AM UTC | 30 days | Encrypted S3/GCS, different region | Monthly restore drill |
> | Database WAL/binlog | Continuous (point-in-time recovery) | 7 days | Same as above | Quarterly |
> | File uploads / media | Daily incremental | 90 days | Separate bucket, versioned | Monthly |
> | Configuration / secrets | On every change | Indefinite | Version-controlled (encrypted) | On change |
> | Full system snapshot | Weekly | 4 weeks | Cloud provider snapshots | Quarterly |
>
> **Disaster recovery plan:**
> - **RPO (Recovery Point Objective)**: How much data can you afford to lose? → drives backup frequency
> - **RTO (Recovery Time Objective)**: How quickly must you recover? → drives recovery strategy
> - **Runbook**: Step-by-step recovery instructions for each failure scenario
> - **Test it**: Untested backups are not backups. Schedule quarterly restore drills.
>
> **Phase 7 — SSL/TLS & Domain:**
>
> - SSL certificate via Let's Encrypt (auto-renewal) or cloud provider
> - HTTPS redirect — all HTTP requests redirect to HTTPS
> - HSTS header — `Strict-Transport-Security: max-age=31536000; includeSubDomains`
> - DNS configuration documentation — A records, CNAME, MX if email
>
> **Phase 8 — Infrastructure as Code (if applicable):**
>
> For production deployments beyond simple PaaS:
> - Terraform / Pulumi / CloudFormation for cloud resources
> - Version-controlled, peer-reviewed, plan-before-apply
> - Separate state per environment
> - Modules for reusable components (VPC, database, load balancer)
>
> **Phase 9 — Documentation:**
>
> Write a `DEPLOYMENT.md` in the project root:
>
> ```markdown
> # Deployment Guide
>
> ## Prerequisites
> [What needs to be installed: Docker, cloud CLI, etc.]
>
> ## Local Development
> [How to start the app locally: docker-compose up, etc.]
>
> ## Environment Variables
> [Table of all env vars: name, description, required, default, example]
>
> ## Deployment
> ### Staging
> [How staging deploys work — auto on merge to develop]
>
> ### Production
> [How production deploys work — process and approvals]
>
> ## Rollback
> [How to rollback to previous version — exact commands]
>
> ## Monitoring
> [Links to dashboards, how to check health, where to find logs]
>
> ## Backup & Recovery
> [How to trigger manual backup, how to restore, who to contact]
>
> ## Troubleshooting
> [Common issues and solutions]
> ```
>
> **Phase 10 — Summary:**
>
> After completing setup, present:
> 1. What was set up (Docker, CI/CD, monitoring, etc.)
> 2. Environment URLs (local, staging, production)
> 3. Dashboard/monitoring links
> 4. Deployment process summary (how code gets to production)
> 5. Rollback procedure (one-liner)
> 6. Backup schedule and recovery time estimate
> 7. Path to `DEPLOYMENT.md`
> 8. Remaining manual steps (DNS configuration, secret rotation, etc.)
> 9. Suggest: "Run a deployment to staging and verify monitoring catches errors before going to production"
>
> **DevOps principles:**
> - **Automate everything repeatable** — if you do it twice, script it
> - **Infrastructure as code** — no manual cloud console changes in production
> - **Immutable deployments** — build once, deploy the same artifact everywhere
> - **Fail gracefully** — health checks, circuit breakers, graceful shutdown
> - **Observe everything** — if you can't see it, you can't fix it
> - **Secure by default** — non-root containers, encrypted connections, rotated secrets
> - **Test the recovery** — untested backups and untested rollbacks are useless
> - **Keep it simple** — Kubernetes is overkill for most apps. Use the simplest infrastructure that meets the requirements. docker-compose for small apps, managed PaaS for medium, orchestrators only when actually needed.
>
> **Reference `csv-cluster-labeler/SKILL.md` for frontmatter format and step-numbering pattern. Make the skill description pushy — trigger on phrases like "deploy", "CI/CD", "Docker", "containerize", "set up pipeline", "monitoring", "devops", "production ready", "infrastructure", "hosting", "deployment", "staging environment", "health check", "alerting", "backup", "disaster recovery", "SSL", "HTTPS", "cloud setup", "rollback", "scale this", "Kubernetes", "docker-compose". No bundled scripts — pure LLM reasoning + infrastructure code generation.**
>
> **Build it. Only ask me if something is genuinely ambiguous.**
