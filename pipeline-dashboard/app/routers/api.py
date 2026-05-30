import io
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from app.config import settings, VERSION
from app.dao import AgentDAO, PipelineDAO, SecurityEventDAO
from app.guardrails import GuardrailsEngine
from app.models import ArtifactInfo, PipelineCreate, ProviderInfo
from app.orchestrator import Orchestrator
from app.providers import ClaudeProvider, GeminiProvider, OllamaProvider

router = APIRouter(prefix="/api")

_providers = {
    "ollama": OllamaProvider(),
    "claude": ClaudeProvider(),
    "gemini": GeminiProvider(),
}
_orchestrator = Orchestrator()
_pipeline_dao = PipelineDAO()
_agent_dao = AgentDAO()
_security_dao = SecurityEventDAO()
_guardrails = GuardrailsEngine()


@router.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "version": VERSION,
        "env": settings.env,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@router.get("/providers")
async def list_providers() -> list[ProviderInfo]:
    results = []
    for name, provider in _providers.items():
        health = await provider.health_check()
        results.append(ProviderInfo(
            name=name,
            available=health.get("available", False),
            models=health.get("models", []),
            error=health.get("error"),
        ))
    return results


@router.get("/providers/{name}/models")
async def provider_models(name: str) -> list[str]:
    provider = _providers.get(name)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return await provider.list_models()


@router.get("/build-profiles")
async def build_profiles() -> JSONResponse:
    from app.config import BUILD_PROFILE_PRESETS
    return JSONResponse({"presets": BUILD_PROFILE_PRESETS})


@router.post("/pipelines")
async def create_pipeline(body: PipelineCreate) -> JSONResponse:
    from app.models import BuildProfile, PipelineRun
    run = PipelineRun(
        project_name=body.project_name,
        description=body.description,
        provider=body.provider,
        model=body.model,
        fast_model=body.fast_model,
        build_profile=body.build_profile or BuildProfile(),
    )
    try:
        run = await _orchestrator.start_pipeline(run)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return JSONResponse({"pipeline": run.model_dump(mode="json")}, status_code=201)


@router.get("/pipelines")
async def list_pipelines(limit: int = 100, offset: int = 0) -> JSONResponse:
    runs = await _pipeline_dao.list_all(limit=limit, offset=offset)
    return JSONResponse({"pipelines": [r.model_dump(mode="json") for r in runs]})


@router.get("/pipelines/current")
async def current_pipeline() -> JSONResponse:
    run = await _pipeline_dao.get_current()
    if not run:
        return JSONResponse({"pipeline": None, "agents": []})
    agents = await _agent_dao.list_by_pipeline(run.id)
    return JSONResponse({
        "pipeline": run.model_dump(mode="json"),
        "agents": [a.model_dump(mode="json") for a in agents],
    })


@router.get("/pipelines/{run_id}")
async def get_pipeline(run_id: UUID) -> JSONResponse:
    try:
        state = await _orchestrator.get_state(run_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return JSONResponse(state)


@router.post("/pipelines/{run_id}/approve")
async def approve_pipeline(run_id: UUID) -> JSONResponse:
    try:
        run = await _orchestrator.approve_checkpoint(run_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return JSONResponse({"pipeline": run.model_dump(mode="json")})


@router.post("/pipelines/{run_id}/feedback")
async def feedback_pipeline(run_id: UUID, feedback: dict) -> JSONResponse:
    text = feedback.get("feedback", "")
    try:
        run = await _orchestrator.submit_feedback(run_id, text)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return JSONResponse({"pipeline": run.model_dump(mode="json")})


@router.post("/pipelines/{run_id}/retry")
async def retry_pipeline(run_id: UUID, body: dict) -> JSONResponse:
    agent_name = body.get("agent", "")
    try:
        run = await _orchestrator.retry_agent(run_id, agent_name)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return JSONResponse({"pipeline": run.model_dump(mode="json")})


@router.delete("/pipelines/{run_id}")
async def delete_pipeline(run_id: UUID) -> JSONResponse:
    await _pipeline_dao.delete(run_id)
    return JSONResponse({"deleted": True})


@router.get("/pipelines/{run_id}/artifacts")
async def list_artifacts(run_id: UUID) -> JSONResponse:
    project_dir = settings.projects_dir / str(run_id)
    if not project_dir.exists():
        return JSONResponse({"artifacts": []})
    artifacts = []
    for root, _dirs, files in os.walk(project_dir):
        for name in files:
            path = Path(root) / name
            rel = str(path.relative_to(project_dir))
            artifacts.append(ArtifactInfo(
                name=name,
                path=rel,
                size=path.stat().st_size,
                is_dir=False,
                modified_at=datetime.fromtimestamp(path.stat().st_mtime),
            ).model_dump(mode="json"))
    return JSONResponse({"artifacts": artifacts})


@router.get("/pipelines/{run_id}/artifacts/{path:path}", response_model=None)
async def get_artifact(run_id: UUID, path: str):
    project_dir = settings.projects_dir / str(run_id)
    target = project_dir / path
    resolved = target.resolve()
    if not str(resolved).startswith(str(project_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not resolved.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")

    suffix = resolved.suffix.lower()
    if suffix in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"):
        return FileResponse(resolved)

    content = resolved.read_text(encoding="utf-8")
    content_type = "text/plain"
    language = None
    if suffix == ".md":
        content_type = "text/markdown"
    elif suffix == ".py":
        language = "python"
    elif suffix in (".js", ".mjs"):
        language = "javascript"
    elif suffix == ".ts":
        language = "typescript"
    elif suffix == ".json":
        language = "json"
    elif suffix in (".yml", ".yaml"):
        language = "yaml"
    elif suffix == ".html":
        language = "html"
    elif suffix == ".css":
        language = "css"
    elif suffix == ".sh":
        language = "bash"
    elif suffix == ".dockerfile":
        language = "dockerfile"

    return JSONResponse({
        "path": path,
        "content": content,
        "content_type": content_type,
        "language": language,
        "size": resolved.stat().st_size,
    })


@router.get("/pipelines/{run_id}/download")
async def download_project(run_id: UUID) -> StreamingResponse:
    project_dir = settings.projects_dir / str(run_id)
    if not project_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(project_dir):
            for name in files:
                path = Path(root) / name
                arcname = str(path.relative_to(project_dir))
                zf.write(path, arcname)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{run_id}.zip"'},
    )


@router.post("/guardrails/reload")
async def reload_guardrails() -> JSONResponse:
    _guardrails.load_config()
    return JSONResponse({"status": "ok", "config": _guardrails._config})


@router.get("/guardrails/events")
async def list_security_events(limit: int = 100) -> JSONResponse:
    events = await _security_dao.list_recent(limit=limit)
    return JSONResponse({"events": [e.model_dump(mode="json") for e in events]})
