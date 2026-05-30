# Deployment Guide

This document covers deploying the SDLC Pipeline Dashboard using process supervisors (systemd, launchd, PM2) and Docker.

## Table of Contents

- [Prerequisites](#prerequisites)
- [systemd (Linux)](#systemd-linux)
- [launchd (macOS)](#launchd-macos)
- [PM2 (Cross-Platform)](#pm2-cross-platform)
- [Docker](#docker)
- [Reverse Proxy (Optional)](#reverse-proxy-optional)

## Prerequisites

Before any deployment method:

1. Install Python 3.12+ and create a virtual environment at `/opt/pipeline-dashboard/.venv` (or your preferred path).
2. Install production dependencies: `pip install -r requirements.txt`
3. Ensure the `projects/`, `data/`, and `logs/` directories exist and are writable.
4. Copy `.env.example` to `.env` and configure as needed.
5. Verify `guardrails.json` exists.

## systemd (Linux)

1. Copy the service unit file:
   ```bash
   sudo cp scripts/systemd/pipeline-dashboard.service /etc/systemd/system/pipeline-dashboard.service
   ```

2. Edit the file to set the correct `User`, `Group`, and `WorkingDirectory` for your installation.

3. Reload systemd and enable the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pipeline-dashboard
   sudo systemctl start pipeline-dashboard
   ```

4. Check status:
   ```bash
   sudo systemctl status pipeline-dashboard
   sudo journalctl -u pipeline-dashboard -f
   ```

5. Restart after updates:
   ```bash
   sudo systemctl restart pipeline-dashboard
   ```

## launchd (macOS)

1. Copy the plist file:
   ```bash
   sudo cp scripts/launchd/com.pipeline-dashboard.plist /Library/LaunchDaemons/
   ```

2. Adjust `WorkingDirectory`, paths, and user permissions as needed.

3. Load and start the service:
   ```bash
   sudo launchctl load /Library/LaunchDaemons/com.pipeline-dashboard.plist
   sudo launchctl start com.pipeline-dashboard
   ```

4. Check status:
   ```bash
   sudo launchctl list | grep pipeline-dashboard
   tail -f /opt/pipeline-dashboard/logs/stdout.log
   ```

5. Unload if needed:
   ```bash
   sudo launchctl unload /Library/LaunchDaemons/com.pipeline-dashboard.plist
   ```

## PM2 (Cross-Platform)

PM2 works on Linux, macOS, and Windows.

1. Install PM2 globally:
   ```bash
   npm install -g pm2
   ```

2. Copy the config:
   ```bash
   cp scripts/pm2/pm2.config.js /opt/pipeline-dashboard/ecosystem.config.js
   ```

3. Start the app:
   ```bash
   cd /opt/pipeline-dashboard
   pm2 start ecosystem.config.js
   ```

4. Save the PM2 process list and configure auto-start on boot:
   ```bash
   pm2 save
   pm2 startup
   ```

5. Monitor:
   ```bash
   pm2 logs pipeline-dashboard
   pm2 monit
   ```

## Docker

### Build and Run with docker-compose

1. Build and start:
   ```bash
   docker compose up --build -d
   ```

2. View logs:
   ```bash
   docker compose logs -f pipeline-dashboard
   ```

3. Stop:
   ```bash
   docker compose down
   ```

### Notes for Docker

- The container exposes port `8000` and binds to `0.0.0.0`.
- `data/`, `projects/`, and `logs/` are mounted as volumes so they persist across container restarts.
- For Ollama, use `host.docker.internal:11434` (macOS/Windows) or the host's LAN IP (Linux). You may need to set `OLLAMA_BASE_URL` accordingly.
- The image runs as a non-root user (`appuser`) for security.

### Standalone Docker

```bash
docker build -t pipeline-dashboard .
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/projects:/app/projects \
  -v $(pwd)/logs:/app/logs \
  -e ENV=prod \
  --name pipeline-dashboard \
  pipeline-dashboard
```

## Reverse Proxy (Optional)

If you want to expose the dashboard to your LAN or Tailscale network, use a reverse proxy with HTTPS:

### Caddy (recommended for local/LAN)

```
pipeline.localhost {
    reverse_proxy 127.0.0.1:8000
    tls internal
}
```

### nginx

```nginx
server {
    listen 443 ssl http2;
    server_name pipeline.localhost;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }
}
```

**Important**: Always bind the backend to `127.0.0.1` (or `0.0.0.0` only behind a trusted reverse proxy). Do not expose port 8000 directly to the public internet without authentication.
