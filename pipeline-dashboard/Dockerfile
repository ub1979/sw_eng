# Multi-stage build for SDLC Pipeline Dashboard
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime image
FROM python:3.12-slim

LABEL org.opencontainers.image.title="SDLC Pipeline Dashboard"
LABEL org.opencontainers.image.description="FastAPI-based SDLC pipeline orchestration dashboard"
LABEL org.opencontainers.image.version="0.1.0"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app/ ./app/
COPY static/ ./static/
COPY guardrails.json .
COPY .env.example .env.example

# Create required directories and set ownership
RUN mkdir -p data projects logs \
    && chown -R appuser:appuser /app

# Copy and process .env if not present at runtime
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Security hardening
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV ENV=prod
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PIPELINE_PROJECTS_DIR=/app/projects
ENV PIPELINE_DATA_DIR=/app/data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check (15s start-period allows DB init + orchestrator startup)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
