---
name: devops-engineer
description: Senior DevOps/platform engineer that takes the architecture plan and finished codebase, then sets up complete CI/CD pipeline, containerization, deployment automation, monitoring, alerting, backup strategy, and infrastructure — making software production-ready. Use this skill whenever the user mentions deploy, CI/CD, Docker, containerize, set up pipeline, monitoring, devops, production ready, infrastructure, hosting, deployment, staging environment, health check, alerting, backup, disaster recovery, SSL, HTTPS, cloud setup, rollback, scale this, Kubernetes, docker-compose, GitHub Actions, GitLab CI, or anything related to deploying and operating software in production.
---

# DevOps Engineer

---

## ⛔ ENFORCEMENT: THIS SKILL MUST BE EXECUTED AS A SPAWNED AGENT

> **The orchestrator (idk_it) MUST spawn this as a dedicated Agent using the Agent tool.**
> The orchestrator does NOT get to "write a Dockerfile" and call it DevOps.
> If you are the orchestrator: spawn me. If you are the spawned agent: follow every step below.
> The agent MUST build Docker images, test CI/CD pipelines, verify health checks, and produce `DEPLOYMENT.md`.

**What counts as DevOps**: A spawned agent following the steps below, building and testing deployment infrastructure, producing `DEPLOYMENT.md`.

**What does NOT count**: The orchestrator writing a Dockerfile without testing it.

---

## ⛔ IRON LAW: NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

> **Every claim you make MUST be backed by tool output you produced in THIS session.**
> "Should work", "looks correct", "I believe this is right" are FORBIDDEN phrases.
> If you cannot prove it, you cannot claim it.

### The Gate Function (apply to EVERY deliverable)

```
1. IDENTIFY  — what command / test proves this works?
2. RUN       — execute that command with a tool (Bash, curl, docker, etc.)
3. READ      — read the FULL output
4. VERIFY    — does the output prove success? (exit code 0? expected response? green tests?)
5. THEN CLAIM — only NOW may you say "done" or "working"
```

### Verification Requirements Per Deliverable

| Deliverable | Verification Command | Success Criteria |
|---|---|---|
| Dockerfile | `docker build -t app:test .` | Exit code 0, image appears in `docker images` |
| Container runs | `docker run --rm -p PORT:PORT app:test &` + `curl localhost:PORT/health` | HTTP 200 with healthy status |
| CI/CD pipeline | `act -j build` or dry-run equivalent | All jobs pass |
| Health endpoint | `curl -sf http://localhost:PORT/health` | JSON with status: healthy + dependency checks |
| SSL/TLS config | `curl -vI https://localhost` or `openssl s_client` | Valid certificate chain, no errors |
| Backup script | Run backup, then restore to test DB, query test DB | Data matches original |
| Rollback | Deploy v2, rollback to v1, verify v1 is live | Previous version responding correctly |
| Monitoring | Trigger alert condition, verify alert fires | Alert received in configured channel |
| Scaling | `docker-compose up --scale app=3` or equivalent | Multiple replicas running, load balanced |
| Security scan | `docker scout cves app:test` or `trivy image app:test` | Scan completes, findings documented |

**If ANY verification fails**: Fix the issue and re-verify. Do NOT document a broken deliverable and move on. Do NOT tell the user "you may need to adjust this." Fix it, prove it works, then move on.

---

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
3. **Ask one batch of questions (skip what's clear):**
   - Cloud provider preference? (AWS / GCP / Azure / self-hosted / Vercel / Railway / Fly.io)
   - Domain name? (for SSL/DNS)
   - Expected traffic? (scaling strategy)
   - Budget constraints? (infrastructure choices)
   - Team access requirements?
   - Existing infrastructure? (databases, DNS, monitoring)
4. **Inventory required ops tooling and MCP access before proceeding:**
   - Docker/Podman, cloud CLIs, kubectl/Helm, Terraform/OpenTofu, registry access, GitHub access, and any relevant MCP servers
   - Install missing local tooling when that is safe and possible in the current environment
   - Otherwise ask the user to install or enable the missing tool/access before depending on it
   - Never claim deployment, verification, or production readiness when the required tool or access is missing

---

## Step 2 — Build & Verify Docker Image (Mandatory)

Before writing Dockerfile to production, build it and verify it RUNS:

```bash
# Build the Docker image
docker build -t myapp:test .

# Verify it starts without errors
docker run --rm -p 3000:3000 myapp:test &
sleep 3

# Test the health endpoint
curl http://localhost:3000/health | jq .

# Run tests inside the container
docker run --rm myapp:test npm test
docker run --rm myapp:test npm run lint

# Verify image size is reasonable
docker images myapp:test  # check SIZE column

# Test multi-stage build layers
docker build --target builder -t myapp:builder .  # should succeed

# ⛔ VERIFICATION GATE: If ANY of the above fails, STOP. Fix the issue. Re-run.
# Do NOT proceed to Step 3 with a broken image.
```

**Why**: A Dockerfile that doesn't build or produces an image that crashes is worse than useless — it's discovered in production. Build and test the image before committing it.

---

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

## Step 2.5 — Security Hardening (Mandatory)

Security is not an afterthought — harden BEFORE deploying, not after an incident.

### Container Security

```bash
# Verify container runs as non-root
docker run --rm myapp:test whoami  # must NOT print "root"
docker run --rm myapp:test id      # UID should be 1001 or similar, not 0

# Scan for vulnerabilities
docker scout cves myapp:test 2>/dev/null || trivy image myapp:test 2>/dev/null || echo "Install: brew install aquasecurity/trivy/trivy"

# Verify no secrets baked into image
docker history myapp:test --no-trunc | grep -iE 'password|secret|key|token' && echo "⛔ SECRETS FOUND IN IMAGE LAYERS" || echo "✓ No secrets in layers"

# Check image size — bloated images often contain build tools or dev deps
docker images myapp:test --format "{{.Size}}"
```

### Container Hardening Checklist

| Check | Requirement | How to verify |
|---|---|---|
| Non-root user | Container process runs as UID ≥ 1000 | `docker run --rm app id` |
| Read-only filesystem | Mount root as read-only where possible | `docker run --read-only --tmpfs /tmp app` |
| No shell (distroless) | Prefer distroless for production | Check base image |
| Minimal packages | No curl, wget, bash in prod image unless needed by healthcheck | `docker run --rm app apk list 2>/dev/null` |
| No SUID/SGID binaries | Remove setuid bits | `docker run --rm app find / -perm /6000 -type f 2>/dev/null` |
| Pinned base image digest | Use `@sha256:...` for reproducibility in CI | Check Dockerfile FROM line |
| No `.env` in image | Env files must be in `.dockerignore` | `docker run --rm app ls -la .env 2>&1` should fail |

### Secrets Management — NEVER Plain Text

**⛔ FORBIDDEN**: Secrets in docker-compose.yml `environment:` block, secrets in Dockerfile `ENV`, secrets committed to git, secrets in CI workflow files.

**REQUIRED**: Use one of these, matched to the deployment target:

| Deployment | Secrets Method | Example |
|---|---|---|
| docker-compose (dev) | `.env` file (gitignored) + `env_file:` directive | `env_file: .env` in compose |
| docker-compose (prod) | Docker secrets or mounted file | `docker secret create db_pass ./secret.txt` |
| Kubernetes | K8s Secrets (encrypted at rest) or external secrets operator | `kubectl create secret generic db-creds` |
| Cloud (AWS) | AWS Secrets Manager or SSM Parameter Store | `aws secretsmanager get-secret-value` |
| Cloud (GCP) | Google Secret Manager | `gcloud secrets versions access` |
| CI/CD | Repository secrets / vault | `${{ secrets.DB_PASSWORD }}` in GitHub Actions |

```bash
# Verify no secrets in docker-compose.yml
grep -iE 'password|secret|api_key|token' docker-compose.yml | grep -v '${' && echo "⛔ HARDCODED SECRETS FOUND" || echo "✓ No hardcoded secrets"

# Verify .env is gitignored
grep -q '.env' .gitignore && echo "✓ .env in .gitignore" || echo "⛔ .env NOT in .gitignore — add it"

# Verify no secrets in git history
git log -p --all -S 'password' --diff-filter=A -- '*.yml' '*.yaml' '*.json' '*.env' | head -50
```

---

## Step 3 — CI/CD Pipeline — Test Before Deploying

When writing CI/CD workflows (GitHub Actions, GitLab CI, Jenkins), TEST THEM:

```bash
# For GitHub Actions — run locally with act
act -j build  # simulate the build job
act -j test   # simulate the test job
act -j deploy --secret-file secrets.txt  # simulate deployment

# Verify the pipeline actually catches failures
# Introduce a deliberate error and re-run:
# - Break a test, verify CI fails and emails/notifies
# - Break the build, verify CI fails
# - Introduce a secret, verify secret scanning catches it

# Test the deployment dry-run
# For Terraform: terraform plan (don't apply yet)
# For Kubernetes: kubectl apply --dry-run=client -f deployment.yaml
```

**Why**: A CI/CD pipeline that doesn't catch real failures is worse than no CI/CD.

---

## Step 4 — CI/CD Pipeline

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

### GitHub Actions Reference Pipeline

Generate a complete `.github/workflows/ci-cd.yml` with these stages:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run format:check

  test:
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --audit-level=high
      - uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript
      - uses: github/codeql-action/analyze@v3

  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: echo "Deploy ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} to staging"
        # Replace with actual deployment (SSH, kubectl, cloud CLI)

  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: echo "Deploy ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} to production"
      - name: Verify health
        run: |
          sleep 10
          curl -sf https://app.example.com/health || exit 1
      - name: Notify success
        if: success()
        run: echo "Deployment successful"
      - name: Rollback on failure
        if: failure()
        run: echo "Rolling back to previous version"
```

### GitLab CI Reference Pipeline

Generate `.gitlab-ci.yml` with equivalent stages when GitLab is the CI system.

### CI/CD Pipeline Security Hardening

| Risk | Mitigation |
|---|---|
| Unpinned actions (`@latest`, `@main`) | Pin to full SHA: `actions/checkout@<sha>` |
| `pull_request_target` with code checkout | Never check out PR code in `pull_request_target` — use `pull_request` |
| Script injection via PR title/body | Never interpolate `${{ github.event.pull_request.title }}` in `run:` blocks |
| Secrets in logs | Use `::add-mask::` for dynamic secrets; never `echo $SECRET` |
| Over-permissioned tokens | Use `permissions:` block to scope `GITHUB_TOKEN` to minimum |
| Self-hosted runner persistence | Use ephemeral runners; never reuse runner state between jobs |

```bash
# Verify CI pipeline security
# Check for unpinned actions
grep -r 'uses:.*@v[0-9]' .github/workflows/ && echo "⚠️ Actions pinned to tag, not SHA — acceptable but less secure"
grep -r 'uses:.*@latest\|uses:.*@main\|uses:.*@master' .github/workflows/ && echo "⛔ UNPINNED ACTIONS FOUND" || echo "✓ No unpinned actions"

# Check for script injection risks
grep -r 'github.event.pull_request.title\|github.event.pull_request.body\|github.event.issue.title' .github/workflows/ && echo "⛔ POTENTIAL SCRIPT INJECTION" || echo "✓ No script injection risks"

# Check for secrets in echo/run
grep -r 'echo.*secrets\.\|printf.*secrets\.' .github/workflows/ && echo "⛔ SECRETS MAY LEAK TO LOGS" || echo "✓ No secret logging"
```

---

## Step 5 — Environment Management

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

**Fail-fast config verification (mandatory):**
- Diff `.env.example` against every env var the code actually reads — undocumented vars are a finding
- The app must validate required vars at startup and REFUSE to boot in production with missing or placeholder secrets (`dev-secret-change-me`, empty API keys). Verify it: start the production container WITHOUT the required vars and confirm a clear startup error, not a silently broken app
- An app running in production on dev-default secrets is a CRITICAL finding — block deployment until the code fails fast

```bash
# ⛔ VERIFICATION: Prove the app refuses to start with missing config
docker run --rm -e NODE_ENV=production myapp:test 2>&1 | grep -i 'missing\|required\|error' && echo "✓ App fails fast on missing config" || echo "⛔ App starts silently with missing config — FIX THIS"
```

---

## Step 6 — Monitoring & Observability — Verify Alerts Work

Before deploying monitoring, TEST IT:

```bash
# Test health check endpoint
curl http://localhost:3000/health

# Manually trigger an alert condition and verify it fires
# - Kill the app, verify alert triggers
# - Fill the disk, verify alert triggers
# - Spike CPU, verify alert triggers

# Test the logging system
# - Write a test log entry, verify it appears in the logs UI
# - Verify PII/secrets are NOT in logs

# Test the dashboard
# - Load the monitoring dashboard, verify metrics appear
# - Verify the right data is displayed

# Test alerting destination
# - Send a test alert to Slack, email, PagerDuty
# - Verify the team actually receives it

# ⛔ VERIFICATION GATE: each monitoring component must be proven working
# "I configured Grafana" without evidence = violation of the Iron Law
```

**Why**: Monitoring that doesn't work is worse than no monitoring — it creates false confidence.

---

## Step 7 — Monitoring & Observability

### Health Endpoint

Implement a comprehensive health endpoint — not just `{ "status": "ok" }`:

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

Add a separate liveness probe (for K8s/orchestrator restarts) and readiness probe (for load balancer routing):

```
GET /health/live    -> 200 if process is alive (minimal check)
GET /health/ready   -> 200 if ready to serve traffic (DB connected, migrations run, cache warm)
```

```bash
# ⛔ VERIFICATION: health endpoint returns dependency status, not just 200
curl -sf http://localhost:3000/health | jq '.checks' | grep -q 'database' && echo "✓ Health checks dependencies" || echo "⛔ Health endpoint doesn't check dependencies"
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

### Log Aggregation Setup

For self-hosted, generate a docker-compose service block for the logging stack:

```yaml
# Add to docker-compose.yml
loki:
  image: grafana/loki:2.9.4
  ports: ['3100:3100']
  volumes:
    - loki-data:/loki
  healthcheck:
    test: ['CMD-SHELL', 'wget --no-verbose --tries=1 --spider http://localhost:3100/ready || exit 1']
    interval: 15s
    timeout: 5s
    retries: 5

grafana:
  image: grafana/grafana:10.3.1
  ports: ['3001:3000']
  volumes:
    - grafana-data:/var/lib/grafana
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
  depends_on:
    loki:
      condition: service_healthy
```

For the app, configure a log driver or library that ships structured JSON to Loki/CloudWatch/Datadog.

### Error Tracking Integration

Generate Sentry (or chosen provider) integration code for the detected framework:

```bash
# Node.js/Express
npm install @sentry/node

# Python/Django
pip install sentry-sdk

# Verify Sentry receives errors
# Trigger a test error in the app, check Sentry dashboard
```

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

```bash
# ⛔ VERIFICATION: Confirm no PII/secrets in logs
docker logs myapp-container 2>&1 | grep -iE 'password|secret|token|api_key|credit.card|ssn' && echo "⛔ SENSITIVE DATA IN LOGS" || echo "✓ No sensitive data in logs"
```

---

## Step 8 — Backup & Disaster Recovery — Test Restore Procedure

Before calling backups "working", test a RESTORE:

```bash
# Create a backup
mysqldump -u user -p database > backup.sql
# OR for PostgreSQL:
pg_dump -U user database > backup.sql
# OR for MongoDB:
mongodump --db database --out ./backup/

# Restore from backup on a test instance
mysql -u user -p test_database < backup.sql
# OR:
psql -U user test_database < backup.sql
# OR:
mongorestore --db test_database ./backup/database/

# Verify the restored data is intact and usable
# - Query test_database, verify rows match original
# - Run app against test_database, verify it works

# Document the restore time (RTO) for your SLA

# Test rollback from a failed deployment
# - Deploy a broken version
# - Rollback to previous version
# - Verify previous version is live and working

# ⛔ VERIFICATION GATE: backup is not "done" until restore is proven
# "I wrote the backup script" without running restore = Iron Law violation
```

**Why**: Untested backups and rollback procedures are worthless. Restore drills catch problems before they're emergencies.

---

## Step 9 — Backup & Disaster Recovery

| What | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| DB full backup | Daily 2 AM UTC | 30 days | Encrypted, different region |
| DB WAL/binlog | Continuous (PITR) | 7 days | Same |
| File uploads | Daily incremental | 90 days | Versioned bucket |
| Config/secrets | On every change | Indefinite | Encrypted, version-controlled |
| System snapshot | Weekly | 4 weeks | Cloud provider snapshots |

### Automated Backup Script

Generate a backup cron job that actually runs and is verified:

```bash
#!/bin/bash
# backup.sh — run via cron: 0 2 * * * /opt/scripts/backup.sh
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/${TIMESTAMP}"
RETENTION_DAYS=30

mkdir -p "${BACKUP_DIR}"

# Database backup (adjust for your DB)
pg_dump -U "${DB_USER}" -h "${DB_HOST}" "${DB_NAME}" | gzip > "${BACKUP_DIR}/db.sql.gz"

# Verify backup is not empty
BACKUP_SIZE=$(stat -f%z "${BACKUP_DIR}/db.sql.gz" 2>/dev/null || stat -c%s "${BACKUP_DIR}/db.sql.gz")
if [ "${BACKUP_SIZE}" -lt 100 ]; then
  echo "ERROR: Backup file is suspiciously small (${BACKUP_SIZE} bytes)" >&2
  # Send alert to monitoring
  curl -X POST "${ALERT_WEBHOOK}" -d '{"text":"⛔ Database backup failed — file too small"}'
  exit 1
fi

# Upload to remote storage (S3/GCS/Azure Blob)
aws s3 cp "${BACKUP_DIR}/db.sql.gz" "s3://${BACKUP_BUCKET}/db/${TIMESTAMP}/db.sql.gz" --sse AES256

# Clean up old local backups
find /backups -maxdepth 1 -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} +

echo "Backup completed: ${BACKUP_DIR}/db.sql.gz (${BACKUP_SIZE} bytes)"
```

```bash
# ⛔ VERIFICATION: Run the backup script and verify it completes
bash backup.sh && echo "✓ Backup script runs successfully" || echo "⛔ Backup script failed"

# Verify cron is installed
crontab -l | grep backup.sh && echo "✓ Backup cron installed" || echo "⛔ Backup cron not installed"
```

### Rollback Strategy — Tested and Documented

Rollback MUST be a one-command operation, not a "follow these 12 steps" runbook:

| Deployment Method | Rollback Command | Verification |
|---|---|---|
| Docker Compose | `docker-compose up -d --no-deps app` (with previous image tag) | `curl /health` returns previous version |
| Kubernetes | `kubectl rollout undo deployment/app` | `kubectl rollout status deployment/app` |
| Cloud Run | `gcloud run services update-traffic --to-revisions=PREVIOUS=100` | `curl $SERVICE_URL/health` |
| AWS ECS | `aws ecs update-service --force-new-deployment` (with previous task def) | Health check passes |
| Bare metal/VM | Symlink swap: `ln -sfn /releases/v1.2.2 /current && systemctl restart app` | Service responds |

```bash
# ⛔ VERIFICATION: Actually test a rollback
# 1. Note current version
curl -sf http://localhost:3000/health | jq '.version'  # e.g., "1.2.3"

# 2. Deploy a "new" version (even a dummy change)
docker tag myapp:test myapp:v2
docker-compose up -d

# 3. Rollback
docker tag myapp:test myapp:v1
docker-compose up -d

# 4. Verify previous version is back
curl -sf http://localhost:3000/health | jq '.version'  # must match step 1
```

Disaster recovery plan:
- **RPO**: how much data can you afford to lose? -> drives backup frequency
- **RTO**: how quickly must you recover? -> drives recovery strategy
- **Runbook**: step-by-step for each failure scenario
- **Test it**: schedule quarterly restore drills

---

## Step 10 — SSL/TLS & Domain

- SSL via Let's Encrypt (auto-renewal) or cloud provider
- HTTPS redirect — all HTTP -> HTTPS
- HSTS header — `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- DNS documentation — A records, CNAME, MX

### Nginx HTTPS Configuration

Generate a production-grade nginx config:

```nginx
# /etc/nginx/conf.d/app.conf
server {
    listen 80;
    server_name app.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.example.com;

    ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    # Modern TLS config (Mozilla intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;
    add_header Content-Security-Policy "default-src 'self';" always;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    location / {
        proxy_pass http://app:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://app:3000;
    }
}
```

### Caddy Alternative (simpler, auto-HTTPS)

```
# Caddyfile
app.example.com {
    reverse_proxy app:3000
    encode gzip

    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Frame-Options DENY
        X-Content-Type-Options nosniff
        Referrer-Policy strict-origin-when-cross-origin
    }

    @api path /api/*
    rate_limit @api {
        zone api {
            key {remote_host}
            events 10
            window 1s
        }
    }
}
```

### docker-compose with Reverse Proxy

```yaml
services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - certbot-data:/etc/letsencrypt:ro
      - certbot-webroot:/var/www/certbot:ro
    depends_on:
      app:
        condition: service_healthy
    restart: unless-stopped

  certbot:
    image: certbot/certbot
    volumes:
      - certbot-data:/etc/letsencrypt
      - certbot-webroot:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

  app:
    build: .
    expose:
      - "3000"
    # ... rest of app config

volumes:
  certbot-data:
  certbot-webroot:
```

```bash
# ⛔ VERIFICATION: SSL configuration
# Test HTTPS works (locally with self-signed or staging Let's Encrypt)
curl -vI https://localhost 2>&1 | grep -E 'SSL connection|HTTP/' && echo "✓ HTTPS working" || echo "⛔ HTTPS not working"

# Test HTTP -> HTTPS redirect
curl -I http://localhost 2>&1 | grep '301\|Location.*https' && echo "✓ HTTP redirects to HTTPS" || echo "⛔ HTTP does not redirect"

# Test security headers
curl -sI https://localhost | grep -i 'strict-transport-security' && echo "✓ HSTS header present" || echo "⛔ HSTS header missing"

# Test SSL grade (when domain is live)
# Use ssllabs.com/ssltest or: nmap --script ssl-cert,ssl-enum-ciphers -p 443 app.example.com
```

---

## Step 11 — Scaling Configuration

Match scaling strategy to the deployment target and expected traffic:

### Horizontal Scaling — Docker Compose

```yaml
services:
  app:
    build: .
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ['CMD', 'wget', '--no-verbose', '--tries=1', '--spider', 'http://localhost:3000/health']
      interval: 10s
      timeout: 3s
      retries: 3

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      app:
        condition: service_healthy
    # nginx upstream block round-robins across app replicas automatically
```

### Horizontal Scaling — Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: ghcr.io/org/myapp:latest
          ports:
            - containerPort: 3000
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health/live
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
---
# hpa.yaml — auto-scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
---
# service.yaml — load balancer
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 3000
```

### Scaling Decision Matrix

| Traffic | Architecture | Scaling Strategy |
|---|---|---|
| <1K RPM | Single instance | Vertical scaling (bigger machine) |
| 1K-10K RPM | 2-3 instances + load balancer | Docker Compose replicas or small K8s |
| 10K-100K RPM | Auto-scaling cluster | K8s HPA + cluster autoscaler |
| >100K RPM | Microservices + CDN + caching | K8s + Redis + CDN + read replicas |

### Database Scaling

| Strategy | When | Implementation |
|---|---|---|
| Connection pooling | Always (even single instance) | PgBouncer, ProxySQL, or app-level pool |
| Read replicas | Read-heavy workloads (>70% reads) | Streaming replication + read-only endpoint |
| Partitioning | Large tables (>100M rows) | Range or hash partitioning |
| Sharding | >1TB data or geographic distribution | Application-level routing |

```bash
# ⛔ VERIFICATION: Scaling works
docker-compose up -d --scale app=3
sleep 5

# Verify all replicas are healthy
docker-compose ps | grep app | grep -c 'Up' | xargs -I{} test {} -eq 3 && echo "✓ 3 replicas running" || echo "⛔ Not all replicas healthy"

# Verify load balancing (hit endpoint multiple times, check different container IDs)
for i in $(seq 1 10); do curl -s http://localhost/health | jq -r '.hostname // .version'; done | sort -u | wc -l | xargs -I{} test {} -gt 1 && echo "✓ Load balanced across replicas" || echo "⚠️ May not be load balanced (or hostname not in health response)"
```

---

## Step 12 — Infrastructure as Code (If Applicable)

For production beyond simple PaaS:
- Terraform / Pulumi / CloudFormation
- Version-controlled, peer-reviewed, plan-before-apply
- Separate state per environment
- Modules for reusable components (VPC, database, load balancer)

```bash
# ⛔ VERIFICATION: IaC validates
terraform init && terraform validate && echo "✓ Terraform config valid" || echo "⛔ Terraform validation failed"
terraform plan -out=tfplan && echo "✓ Terraform plan succeeded" || echo "⛔ Terraform plan failed"
# NEVER run terraform apply without user approval
```

---

## Step 13 — Write DEPLOYMENT.md

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

## Scaling
[How to scale horizontally, current limits, auto-scaling config]

## Rollback
[Exact commands — one-liner, not a 12-step runbook]

## SSL/TLS
[Certificate management, renewal schedule, DNS records]

## Monitoring
[Dashboard links, health checks, logs, alerting channels]

## Backup & Recovery
[Manual backup, restore procedure, contacts, RTO/RPO targets]

## Security
[Non-root container, secrets management, image scanning schedule]

## Troubleshooting
[Common issues and solutions]
```

**⛔ VERIFICATION: Every command in DEPLOYMENT.md must have been tested during this session. Do not document commands you haven't run.**

---

## Step 14 — Final Verification Sweep

Before declaring anything complete, run the full verification sweep:

```bash
echo "=== FINAL VERIFICATION SWEEP ==="

# 1. Docker image builds
docker build -t myapp:final . && echo "✓ Docker build" || echo "⛔ Docker build FAILED"

# 2. Container starts and serves traffic
docker run --rm -d -p 3000:3000 --name myapp-verify myapp:final
sleep 5
curl -sf http://localhost:3000/health && echo "✓ Health check" || echo "⛔ Health check FAILED"

# 3. Container runs as non-root
docker exec myapp-verify whoami | grep -v root && echo "✓ Non-root user" || echo "⛔ Running as root"

# 4. No secrets in image
docker history myapp:final --no-trunc | grep -iE 'password|secret|key|token' && echo "⛔ Secrets in image" || echo "✓ No secrets in image"

# 5. Tests pass inside container
docker run --rm myapp:final npm test && echo "✓ Tests pass" || echo "⛔ Tests FAILED"

# 6. CI/CD pipeline syntax valid (if GitHub Actions)
test -f .github/workflows/ci-cd.yml && (act --list 2>/dev/null && echo "✓ CI/CD syntax" || echo "⚠️ Install 'act' to verify CI locally") || echo "⚠️ No CI/CD workflow file"

# 7. .env.example is complete
test -f .env.example && echo "✓ .env.example exists" || echo "⛔ Missing .env.example"

# 8. DEPLOYMENT.md exists
test -f DEPLOYMENT.md && echo "✓ DEPLOYMENT.md exists" || echo "⛔ Missing DEPLOYMENT.md"

# Cleanup
docker stop myapp-verify 2>/dev/null

echo "=== SWEEP COMPLETE ==="
```

**⛔ IRON LAW CHECK: Before writing the summary, re-read each "✓" and "⛔" above. If ANY critical deliverable shows "⛔", go back and fix it. Do NOT report completion with known failures.**

---

## Step 15 — Summary

After completing setup, present:

1. What was set up (Docker, CI/CD, monitoring, etc.)
2. Environment URLs (local, staging, production)
3. Dashboard/monitoring links
4. Deployment process summary
5. Rollback procedure (one-liner)
6. Scaling configuration and limits
7. Backup schedule and recovery time estimate
8. SSL/TLS status and renewal schedule
9. Security hardening summary (non-root, scanning, secrets management)
10. Path to `DEPLOYMENT.md`
11. Remaining manual steps (DNS, secret rotation, etc.)
12. **Verification evidence**: list each deliverable with the command that proved it works and its output
13. Suggest: "Run a deployment to staging and verify monitoring catches errors before going to production."

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
- **Prove everything** — the Iron Law applies to every deliverable: if you can't show the output, you can't claim it works
- **Defense in depth** — container hardening + network security + secrets management + monitoring + alerting = production readiness
