# API Reference

The SDLC Pipeline Dashboard exposes a REST API for state-changing operations and data fetching, plus a Server-Sent Events (SSE) stream for real-time updates.

## Interactive Documentation

When the server is running in `dev` mode, interactive OpenAPI docs are available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

In `prod` mode, these endpoints are disabled for security.

## Authentication

MVP has no authentication. The app binds to `127.0.0.1:8000` by default and is only accessible from the local machine. Future versions will add JWT cookie-based auth.

## REST Endpoints

### Health

| | |
|---|---|
| `GET /api/health` | Liveness probe |

**Response**:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "database": "connected"
}
```

### Providers

| | |
|---|---|
| `GET /api/providers` | List configured providers with health status |

**Response**:
```json
[
  {
    "name": "ollama",
    "available": true,
    "models": ["llama3.2", "codellama"],
    "error": null
  }
]
```

| | |
|---|---|
| `GET /api/providers/{name}/models` | List available models for a provider |

### Pipelines

| | |
|---|---|
| `POST /api/pipelines` | Start a new pipeline |

**Request body** (`PipelineCreate`):
```json
{
  "project_name": "My Portfolio",
  "description": "I want a portfolio website...",
  "provider": "ollama",
  "model": "llama3.2"
}
```

| | |
|---|---|
| `GET /api/pipelines` | List all pipeline runs (history) |

| | |
|---|---|
| `GET /api/pipelines/current` | Get the active or most recent pipeline |

| | |
|---|---|
| `GET /api/pipelines/{id}` | Get pipeline details and agent statuses |

| | |
|---|---|
| `POST /api/pipelines/{id}/approve` | Approve checkpoint and continue |

| | |
|---|---|
| `POST /api/pipelines/{id}/feedback` | Submit change request at checkpoint |

**Request body**:
```json
{
  "feedback": "Use PostgreSQL instead of SQLite."
}
```

| | |
|---|---|
| `POST /api/pipelines/{id}/retry` | Retry a failed agent |

**Request body**:
```json
{
  "agent_name": "sw_developer"
}
```

| | |
|---|---|
| `DELETE /api/pipelines/{id}` | Delete pipeline and its folder |

### Artifacts

| | |
|---|---|
| `GET /api/pipelines/{id}/artifacts` | List artifacts with metadata |

**Response**:
```json
[
  {
    "name": "requirements.md",
    "path": "requirements.md",
    "size": 1240,
    "is_dir": false,
    "modified_at": "2026-05-28T10:00:00"
  }
]
```

| | |
|---|---|
| `GET /api/pipelines/{id}/artifacts/{path}` | View/download a single artifact |

| | |
|---|---|
| `GET /api/pipelines/{id}/download` | Download entire project as ZIP |

### Guardrails

| | |
|---|---|
| `POST /api/guardrails/reload` | Reload `guardrails.json` config |

| | |
|---|---|
| `GET /api/guardrails/events` | List recent security events |

**Response**:
```json
[
  {
    "id": "...",
    "pipeline_id": "...",
    "timestamp": "2026-05-28T10:00:00",
    "event_type": "blocked_command",
    "detail": "Executable 'sudo' not in allowlist",
    "command": "sudo apt-get update"
  }
]
```

## Server-Sent Events (SSE)

| | |
|---|---|
| `GET /api/pipelines/{id}/events` | SSE stream for real-time updates |

Connect with a browser-native `EventSource`:

```javascript
const source = new EventSource(`/api/pipelines/${pipelineId}/events`);
source.addEventListener("message", (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.payload);
});
```

### SSE Event Types

| Event Type | Description | Payload |
|-----------|-------------|---------|
| `sync` | Full state burst sent on reconnect | `{ pipeline, agents, logs }` |
| `agent_start` | An agent began execution | `{ agent, pipeline }` |
| `log` | A log line from the active agent | `{ agent, line }` |
| `checkpoint` | Pipeline paused for approval | `{ agent, artifact_path, pipeline }` |
| `complete` | Pipeline finished successfully | `PipelineRun` JSON |
| `error` | Pipeline or agent failure | `{ detail, suggestion? }` |
| `security_event` | Guardrails blocked a command | `SecurityEvent` JSON |

### Reconnect Behavior

The browser `EventSource` auto-reconnects with exponential backoff. On each new SSE connection, the backend sends a `sync` event containing the full current pipeline state, agent statuses, and the last 100 log lines so the UI catches up instantly.

## Rate Limits

MVP does not implement formal rate limiting. Recommended limits for future scaling:

- General API: 10 requests/second per IP
- Pipeline starts: 1 per minute
- Checkpoint approvals: 5 per minute

## Error Responses

All errors return JSON with detail:

```json
{
  "detail": "A pipeline is already running or paused at a checkpoint."
}
```

Common status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad Request (Pydantic validation error) |
| 404 | Pipeline or artifact not found |
| 409 | Conflict (pipeline already running) |
| 422 | Unprocessable Entity (invalid input) |
| 500 | Internal server error |
