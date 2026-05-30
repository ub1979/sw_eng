# Deployment Guide

This document covers production deployment procedures for the SDLC Pipeline Dashboard.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Linux Server (systemd)](#linux-server-systemd)
6. [macOS (launchd)](#macos-launchd)
7. [Cross-Platform (PM2)](#cross-platform-pm2)
8. [Health Checks & Monitoring](#health-checks--monitoring)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The SDLC Pipeline Dashboard is a FastAPI application backed by SQLite (with WAL mode). Because SQLite has limited concurrent write throughput, the application is designed to run as a **single-worker process**. Scale horizontally (multiple container/service instances) only if each instance uses its own isolated SQLite database and project directory.

### Production Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment created and dependencies installed
- [ ] `.env` configured for production (`ENV=prod`)
- [ ] `guardrails.json` reviewed and hardened
- [ ] `data/`, `projects/`, and `logs/` directories exist and are writable
- [ ] Reverse proxy (nginx, Caddy, Traefik) configured with TLS if exposed to the internet
- [ ] Health check script tested
- [ ] Log rotation configured

---

## Prerequisites

- **Python 3.12+**
- **pip** and **venv**
- (Optional) **Docker** 20.10+ and **Docker Compose** v2+
- (Optional) **Node.js / npm** for projects the pipeline itself generates
- One or more AI model providers (Ollama, Claude CLI, Gemini CLI)

---

## Local Development

The fastest way to run the application locally is with `make run` or the provided startup script.

### Using Make

```bash
# Install dependencies
make install-dev

# Start development server with auto-reload
make run

# Start production-like server (no reload)
make run-prod
```

The server binds to `127.0.0.1:8000` by default. Open **http://localhost:8000**.

### Using the Startup Script

```bash
# Development mode (auto-reload, dev dependencies)
./scripts/start.sh dev

# Production mode
./scripts/start.sh prod
```

The script automatically:
- Checks the Python version (requires 3.12+)
- Creates/activates a `.venv` if missing
- Installs the correct dependency set
- Creates required directories (`data/`, `projects/`, `logs/`)
- Seeds `.env` from `.env.example` if missing
- Seeds a default `guardrails.json` if missing

---

## Docker Deployment

### Build

```bash
docker build -t pipeline-dashboard:latest .
```

The Dockerfile uses a multi-stage build:
1. **Builder stage** installs Python dependencies into a virtual environment.
2. **Runtime stage** copies the venv, application code, and static assets. It runs as a non-root user (`appuser`) for security.

### Run

```bash
docker run -d \
  --name pipeline-dashboard \
  -p 8000:8000 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/projects:/app/projects" \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/guardrails.json:/app/guardrails.json:ro" \
  -e ENV=prod \
  -e DATABASE_URL=sqlite+aiosqlite:///data/pipeline.db \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  pipeline-dashboard:latest
```

### Docker Compose

A `docker-compose.yml` is provided in the project root.

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f pipeline-dashboard

# Stop
docker-compose down
```

#### Linux Note

`host.docker.internal` is automatically available on Docker Desktop (macOS/Windows). On Linux Docker Engine, the Compose file includes an `extra_hosts` entry to map it to the host gateway. If your Ollama server runs on a different host or port, override `OLLAMA_BASE_URL`:

```bash
OLLAMA_BASE_URL=http://192.168.1.50:11434 docker-compose up -d
```

#### Health Check

The container includes a Docker `HEALTHCHECK` that polls `/api/health` every 30 seconds. You can inspect it with:

```bash
docker inspect --format='{{.State.Health.Status}}' pipeline-dashboard
```

---

## Linux Server (systemd)

### 1. Install Application

```bash
sudo mkdir -p /opt/pipeline-dashboard
sudo cp -r . /opt/pipeline-dashboard/
cd /opt/pipeline-dashboard

sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt

sudo mkdir -p data projects logs
sudo cp .env.example .env
```

Edit `/opt/pipeline-dashboard/.env` for production:

```bash
ENV=prod
HOST=127.0.0.1
PORT=8000
```

### 2. Install Service

The service file is a **template unit** that expects a username as an instance parameter.

```bash
sudo cp scripts/systemd/pipeline-dashboard.service \
     /etc/systemd/system/pipeline-dashboard@.service

# Reload systemd
sudo systemctl daemon-reload

# Start and enable for user 'pipeline'
sudo systemctl enable pipeline-dashboard@pipeline
sudo systemctl start pipeline-dashboard@pipeline
```

If you prefer a hardcoded user instead of the `%I` template syntax, edit the service file and replace `User=%I` / `Group=%I` with concrete values (e.g., `User=pipeline`).

### 3. Manage Service

```bash
# Status
sudo systemctl status pipeline-dashboard@pipeline

# Logs
sudo journalctl -u pipeline-dashboard@pipeline -f

# Restart
sudo systemctl restart pipeline-dashboard@pipeline

# Stop
sudo systemctl stop pipeline-dashboard@pipeline
```

### 4. Reverse Proxy (Recommended)

Bind the app to `127.0.0.1` and expose it through nginx or Caddy with TLS:

**nginx example:**

```nginx
server {
    listen 443 ssl http2;
    server_name pipeline.example.com;

    ssl_certificate /etc/letsencrypt/live/pipeline.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pipeline.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## macOS (launchd)

### 1. Install Application

```bash
sudo mkdir -p /opt/pipeline-dashboard
sudo cp -r . /opt/pipeline-dashboard/
cd /opt/pipeline-dashboard

sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt

sudo mkdir -p data projects logs
sudo cp .env.example .env
```

Edit `.env` for production as shown in the Linux section.

### 2. Install Service

```bash
sudo cp scripts/launchd/com.pipeline-dashboard.plist \
     /Library/LaunchDaemons/com.pipeline-dashboard.plist

# Load
sudo launchctl load /Library/LaunchDaemons/com.pipeline-dashboard.plist

# Start
sudo launchctl start com.pipeline-dashboard
```

### 3. Manage Service

```bash
# Status
sudo launchctl list com.pipeline-dashboard

# Stop
sudo launchctl stop com.pipeline-dashboard

# Unload completely
sudo launchctl unload /Library/LaunchDaemons/com.pipeline-dashboard.plist
```

### 4. Logs

launchd writes stdout and stderr to:

- `/opt/pipeline-dashboard/logs/stdout.log`
- `/opt/pipeline-dashboard/logs/stderr.log`

Ensure the `logs/` directory exists before loading the service, or create it immediately after installation.

---

## Cross-Platform (PM2)

PM2 works on Linux, macOS, and Windows and provides log management, auto-restart, and clustering controls.

### 1. Install PM2

```bash
npm install -g pm2
```

### 2. Install Application

Follow the same application installation steps as the Linux/macOS sections, placing the project at `/opt/pipeline-dashboard` (or any directory of your choice).

### 3. Start with PM2

```bash
cd /opt/pipeline-dashboard

# Production mode
pm2 start scripts/pm2/pm2.config.js --env production

# Development mode
pm2 start scripts/pm2/pm2.config.js
```

### 4. Manage Process

```bash
pm2 status
pm2 logs pipeline-dashboard
pm2 restart pipeline-dashboard
pm2 stop pipeline-dashboard
pm2 delete pipeline-dashboard

# Save PM2 config to restart on boot
pm2 save
pm2 startup
```

### 5. Log Rotation (Optional)

```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 100M
pm2 set pm2-logrotate:retain 10
```

---

## Health Checks & Monitoring

### Built-In Health Endpoint

The application exposes a health check at:

```
GET /api/health
```

Example response:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "env": "prod",
  "timestamp": "2026-05-29T12:34:56.789000+00:00"
}
```

### Health Check Script

A shell script is provided at `scripts/health-check.sh`:

```bash
# Check localhost
./scripts/health-check.sh

# Check a remote host
./scripts/health-check.sh 192.168.1.50 8000
```

The script verifies:
1. The `uvicorn` process is running
2. `/api/health` returns HTTP 200
3. Disk usage is below 90%
4. `.env` file exists

### Supervisor-Specific Health Checks

| Supervisor | Health Check Method |
|------------|---------------------|
| Docker | Built-in `HEALTHCHECK` polls `/api/health` every 30s |
| systemd | Use `systemctl status` + `scripts/health-check.sh` in a timer unit or external monitor |
| launchd | Use `launchctl list` + `scripts/health-check.sh` |
| PM2 | Use `pm2 status` + PM2's built-in monitoring (`pm2 monit`) |

### Monitoring Setup

For production monitoring, integrate one or more of the following:

1. **Uptime Checks**
   - Configure an external uptime monitor (e.g., Uptime Kuma, Pingdom, Datadog Synthetics) to poll `https://<host>/api/health` every 60 seconds.

2. **Log Aggregation**
   - systemd: forward journald logs to Grafana Loki or Datadog via `systemd-journal-gatewayd` or a log shipper.
   - Docker: use the `json-file` or `journald` log driver, or sidecar a Fluent Bit container.
   - PM2: use `pm2 logs` piped to a log shipper, or configure `pm2-logrotate` and ship rotated files.

3. **Resource Monitoring**
   - Use `node_exporter` (Prometheus) or the Datadog Agent to monitor CPU, memory, and disk of the host running the application.
   - Alert when disk usage exceeds 80% (SQLite WAL files can grow during heavy pipeline runs).

4. **Alerting Rules**
   - Health endpoint down for > 2 minutes
   - Disk usage > 85%
   - Process restart loop (> 3 restarts in 5 minutes)

### Database Backups

The application automatically creates timestamped SQLite backups under `data/backups/` (up to 20 retained). For additional safety, back up the entire `data/` directory nightly:

```bash
# Example cron job
0 2 * * * tar czf /backups/pipeline-data-$(date +\%Y\%m\%d).tar.gz /opt/pipeline-dashboard/data
```

---

## Troubleshooting

### Docker Build

If you see `Cannot connect to the Docker daemon`, ensure the Docker Engine is running:

```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Service Won't Start

1. Check permissions on `data/`, `projects/`, and `logs/`.
2. Verify `.env` values (especially `DATABASE_URL` and `PIPELINE_PROJECTS_DIR`).
3. Check that the virtual environment exists and contains `uvicorn`:
   ```bash
   .venv/bin/python -m uvicorn --version
   ```

### Database Locked / WAL Growth

SQLite WAL mode is enabled. Under normal load the WAL auto-checkpoints. If the WAL grows very large:

1. Restart the application (this triggers a checkpoint).
2. Run a manual checkpoint:
   ```bash
   sqlite3 data/pipeline.db "PRAGMA wal_checkpoint(TRUNCATE);"
   ```

### SSE / Live Updates Not Working Behind a Proxy

If you place the app behind nginx or another reverse proxy, ensure the proxy supports SSE streaming:

```nginx
proxy_buffering off;
proxy_cache off;
```

### Ollama Not Reachable from Docker

If the app is containerized and Ollama runs on the Docker host, confirm the correct `OLLAMA_BASE_URL`:

- Docker Desktop (macOS/Windows): `http://host.docker.internal:11434`
- Linux Docker Engine: `http://172.17.0.1:11434` (default bridge gateway) or the host's LAN IP.

---

## File Locations

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage production image |
| `docker-compose.yml` | Compose stack definition |
| `scripts/start.sh` | Local startup helper |
| `scripts/health-check.sh` | Runtime health verification |
| `scripts/systemd/pipeline-dashboard.service` | systemd template unit |
| `scripts/launchd/com.pipeline-dashboard.plist` | macOS LaunchDaemon |
| `scripts/pm2/pm2.config.js` | PM2 ecosystem file |
