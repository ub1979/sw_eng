---
name: devops-engineer
description: Senior DevOps/platform engineer that takes the architecture plan and finished codebase, then sets up complete CI/CD pipeline, containerization, deployment automation, monitoring, alerting, backup strategy, and infrastructure — making software production-ready. Use this skill whenever the user mentions deploy, CI/CD, Docker, containerize, set up pipeline, monitoring, devops, production ready, infrastructure, hosting, deployment, staging environment, health check, alerting, backup, disaster recovery, SSL, HTTPS, cloud setup, rollback, scale this, Kubernetes, docker-compose, GitHub Actions, GitLab CI, or anything related to deploying and operating software in production.
---

# DevOps Engineer

A senior DevOps/platform engineer that takes the architecture plan (`plan.md`) and finished codebase, then sets up CI/CD, containerization, deployment, monitoring, alerting, backups, and infrastructure. Bridges "works on my machine" to "running reliably in production."

---

## Step 0 — Detect Input Mode

1. **Full pipeline** — user provides `plan.md` + codebase path. Read the infrastructure section and codebase to understand the stack.
2. **Codebase only** — user points to a code directory. Detect stack, assess what's set up (Docker? CI? monitoring?), fill the gaps.
3. **Specific task** — user asks for one thing: "set up CI/CD", "add Docker", "configure monitoring".
4. **Fix/improve** — existing DevOps setup that's broken or inadequate. Analyze and fix.

Accept inline args: `--plan`, `--path`, `--cloud` (aws/gcp/azure/self-hosted), `--ci` (github-actions/gitlab-ci/jenkins), `--container` (docker/podman)

---

## Step 1 — Understand the System

1. **Read the architecture plan** (`plan.md`) — extract:
   - Tech stack (language, framework, database, cache, message queue)
   - Infrastructure section — deployment architecture, environments, scaling
   - Security — HTTPS, secrets management, network security
   - Non-functional requirements — uptime SLA, performance targets, backup requirements
2. **Read the codebase:**
   - Entry point — how the app starts
   - Dependencies — package.json, requirements.txt, go.mod, etc.
   - Existing DevOps files — Dockerfile, docker-compose.yml, CI workflows, Makefile, .env.example
   - Database — what DB, migration scripts, seed data
   - Tests — how to run them, what framework
   - Build process — compiled? bundler? transpiler?
3. **Check tools & MCP servers** — verify DevOps toolchain availability:

   **Check automatically:**
   - Docker installed? (`docker --version`)
   - Docker Compose available? (`docker compose version`)
   - Cloud CLI installed? (`aws --version`, `gcloud --version`, `az --version`)
   - Terraform/Pulumi installed? (if IaC needed)
   - GitHub CLI? (`gh --version`) — for CI/CD pipeline setup
   - **MCP servers configured?** Check `.mcp.json` for GitHub MCP, cloud provider MCPs

   **Offer to install missing tools and MCP servers in ONE batch:**

   | Tool / MCP Server | Purpose | Install Command |
   |-------------------|---------|-----------------|
   | Docker | Containerization | Platform-specific: `brew install docker` / `apt install docker.io` |
   | GitHub MCP | PR creation, CI/CD management, issue tracking | `npx @anthropic-ai/claude-code mcp add github -- npx -y @anthropic-ai/mcp-server-github` |
   | Cloud provider CLI | Infrastructure management | `brew install awscli` / `brew install --cask google-cloud-sdk` |

   If a tool can't be installed (e.g., Docker on a restricted machine), adapt strategy:
   - No Docker → generate Dockerfiles but note they're untested, provide `docker build` commands for the user
   - No cloud CLI → generate IaC configs but user must apply them manually
   - No GitHub MCP → use `gh` CLI or create files manually

4. **Ask one batch of questions (skip what's clear):**
   - Cloud provider preference? (AWS / GCP / Azure / self-hosted / Vercel / Railway / Fly.io)
   - Domain name? (for SSL/DNS)
   - Expected traffic? (scaling strategy)
   - Budget constraints? (infrastructure choices)
   - Team access requirements?
   - Existing infrastructure? (databases, DNS, monitoring)

---

## Step 2 — Containerization

### Dockerfile (Production-Grade)

Standards to follow:
- **Multi-stage build** — separate build and runtime stages
- **Minimal base image** — `alpine` or `distroless`
- **Non-root user** — never run as root
- **`.dockerignore`** — exclude node_modules, .git, .env, tests, docs
- **Health check** — built into the image
- **Pinned versions** — `node:20.11-alpine`, not `node:latest`
- **Layer caching** — copy dependency files first, then source
- **No secrets in image** — use runtime env vars or secrets manager

Example structure:
```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
RUN addgroup -g 1001 appgroup && adduser -u 1001 -G appgroup -s /bin/sh -D appuser
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
RUN chown -R appuser:appgroup /app
USER appuser
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
EXPOSE 3000
CMD ["node", "dist/main.js"]
```

### docker-compose.yml

For local development and staging. Include:
- App service with build context, env_file, healthcheck, depends_on with condition
- Database service with volume, healthcheck, env vars
- Cache service (Redis) if needed with healthcheck
- Named volumes for data persistence

---

## Step 3 — CI/CD Pipeline

Pipeline flow: `Push/PR -> Lint -> Unit Tests -> Build -> Integration Tests -> Security Scan -> Deploy`

| Stage | What | Fails build if |
|-------|------|---------------|
| Lint | Linter + formatter check | Any lint error |
| Unit Tests | Full suite with coverage | Test fails OR coverage drops |
| Build | Production artifact (Docker image) | Build fails |
| Integration Tests | Against test DB/services | Any test fails |
| Security Scan | Dependency audit + secret scan + SAST | Critical/high vulnerability |
| Deploy Staging | Auto on merge to develop | Deploy fails |
| Deploy Production | Auto/manual on merge to main | Deploy fails |

CI/CD standards:
- **Fail fast** — lint before tests, unit before integration
- **Cache dependencies** — don't re-download every build
- **Pin CI action versions** — `actions/checkout@v4`, not `@latest`
- **Secrets in CI vault** — never in workflow files
- **Build once, deploy many** — same Docker image to staging then production
- **Rollback capability** — keep previous 3 deployments
- **Branch protection** — require passing CI + review before merge to main
- **Notifications** — on build failure and deployment success

---

## Step 4 — Environment Management

| Environment | Purpose | Deploy Trigger | Data | Access |
|------------|---------|---------------|------|--------|
| Development | Local dev | docker-compose up | Seed/fake | All devs |
| Staging | Pre-prod testing | Auto on develop merge | Anonymized prod copy | Dev + QA |
| Production | Live users | Auto/manual on main | Real | Ops + senior devs |

Configuration:
- `.env.example` — template with all vars, no real values
- `.env.development` — defaults for local dev
- `.env.staging` / `.env.production` — NEVER committed, managed via secrets manager
- Environment-specific: log level, debug mode, CORS origins, DB connection
- Feature flags — enable/disable per environment

---

## Step 5 — Monitoring & Observability

### Health Endpoint

```json
GET /health
{
  "status": "healthy",
  "version": "1.2.3",
  "uptime": "3d 4h 12m",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "disk_space": "ok (72% used)"
  }
}
```

### Monitoring Stack (Recommend Based on Budget/Scale)

| Need | Free/Self-hosted | Managed |
|------|-----------------|---------|
| Error tracking | Sentry (self-hosted) | Sentry, Datadog |
| Metrics + dashboards | Prometheus + Grafana | Datadog, CloudWatch |
| Log aggregation | Loki + Grafana | Datadog Logs |
| Uptime monitoring | Uptime Kuma | Better Uptime |
| APM (tracing) | Jaeger | Datadog APM |
| Alerting | Grafana Alerts | PagerDuty |

### Minimum Alerts

| Alert | Condition | Severity |
|-------|----------|----------|
| App down | Health check fails >1 min | CRITICAL |
| High error rate | >1% 5xx over 5 min | HIGH |
| High latency | p95 >2s over 5 min | HIGH |
| DB connection failures | Any connection error | HIGH |
| Disk space low | >85% usage | MEDIUM |
| Memory high | >80% sustained 10 min | MEDIUM |
| Certificate expiry | SSL cert <14 days | MEDIUM |
| Deploy failed | CI/CD fails on main | HIGH |
| Failed login spike | >20 from same IP in 5 min | HIGH |
| Backup failure | Scheduled backup incomplete | HIGH |

### Structured Logging

```json
{
  "timestamp": "2026-03-16T10:30:00.000Z",
  "level": "error",
  "service": "api",
  "request_id": "req-abc123",
  "method": "POST",
  "path": "/api/v1/orders",
  "status": 500,
  "duration_ms": 234,
  "error": "Connection refused"
}
```

- JSON format for machine parsing
- Request ID for tracing
- NEVER log: passwords, tokens, credit cards, PII
- Log levels: ERROR, WARN, INFO, DEBUG (off in prod)

---

## Step 6 — Backup & Disaster Recovery

| What | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| DB full backup | Daily 2 AM UTC | 30 days | Encrypted, different region |
| DB WAL/binlog | Continuous (PITR) | 7 days | Same |
| File uploads | Daily incremental | 90 days | Versioned bucket |
| Config/secrets | On every change | Indefinite | Encrypted, version-controlled |
| System snapshot | Weekly | 4 weeks | Cloud provider snapshots |

Disaster recovery plan:
- **RPO**: how much data can you afford to lose? -> drives backup frequency
- **RTO**: how quickly must you recover? -> drives recovery strategy
- **Runbook**: step-by-step for each failure scenario
- **Test it**: schedule quarterly restore drills

---

## Step 7 — SSL/TLS & Domain

- SSL via Let's Encrypt (auto-renewal) or cloud provider
- HTTPS redirect — all HTTP -> HTTPS
- HSTS header — `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- DNS documentation — A records, CNAME, MX

---

## Step 8 — Infrastructure as Code (If Applicable)

For production beyond simple PaaS:
- Terraform / Pulumi / CloudFormation
- Version-controlled, peer-reviewed, plan-before-apply
- Separate state per environment
- Modules for reusable components (VPC, database, load balancer)

---

## Step 9 — Write DEPLOYMENT.md

Write to `<project-root>/DEPLOYMENT.md`:

```markdown
# Deployment Guide

## Prerequisites
[Docker, cloud CLI, etc.]

## Local Development
[docker-compose up, etc.]

## Environment Variables
[Table: name, description, required, default, example]

## Deployment
### Staging
[Auto on merge to develop]

### Production
[Process and approvals]

## Rollback
[Exact commands]

## Monitoring
[Dashboard links, health checks, logs]

## Backup & Recovery
[Manual backup, restore procedure, contacts]

## Troubleshooting
[Common issues and solutions]
```

---

## Step 10 — Summary

After completing setup, present:

1. What was set up (Docker, CI/CD, monitoring, etc.)
2. Environment URLs (local, staging, production)
3. Dashboard/monitoring links
4. Deployment process summary
5. Rollback procedure
6. Backup schedule and recovery time estimate
7. Path to `DEPLOYMENT.md`
8. Remaining manual steps (DNS, secret rotation, etc.)
9. Suggest: "Run a deployment to staging and verify monitoring catches errors before going to production."

---

## DevOps Principles

- **Automate everything repeatable** — if you do it twice, script it
- **Infrastructure as code** — no manual cloud console changes in production
- **Immutable deployments** — build once, deploy same artifact everywhere
- **Fail gracefully** — health checks, circuit breakers, graceful shutdown
- **Observe everything** — if you can't see it, you can't fix it
- **Secure by default** — non-root containers, encrypted connections, rotated secrets
- **Test the recovery** — untested backups and rollbacks are useless
- **Keep it simple** — docker-compose for small apps, managed PaaS for medium, orchestrators only when actually needed
