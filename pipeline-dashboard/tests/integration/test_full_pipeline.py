import asyncio
import pytest
import pytest_asyncio
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.database import get_db_path
from app.models import StreamChunk
from app.providers import LLMProvider


@pytest_asyncio.fixture
async def async_client(monkeypatch, tmp_path):
    db_dir = tmp_path / "data"
    db_dir.mkdir()
    db_path = db_dir / "pipeline.db"

    async def override_get_db_path():
        return str(db_path)

    monkeypatch.setattr("app.database.get_db_path", override_get_db_path)

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setenv("PIPELINE_PROJECTS_DIR", str(projects_dir))

    from app.database import init_database
    await init_database()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    if db_path.exists():
        db_path.unlink()


class DeterministicProvider(LLMProvider):
    name = "mock"

    def __init__(self, content_map=None):
        self._content_map = content_map or {}
        self._default = "# Output\n\nGeneric output"

    async def chat(self, messages, stream=True):
        all_text = " ".join(m.get("content", "") for m in messages)
        content = self._default
        for key, val in self._content_map.items():
            if key in all_text.lower():
                content = val
                break
        yield StreamChunk(content=content, done=True)

    async def list_models(self):
        return []

    async def health_check(self):
        return {"available": True, "models": [], "error": None}


def make_provider():
    return DeterministicProvider({
        "requirements engineer": "# Requirements\n\nTest requirements",
        "software architect": "# Architecture Plan\n\nPython + FastAPI",
        "project manager": "# Project Plan\n\nEpic 1: Build",
        "senior software developer": "--- FILE: src/main.py ---\nprint('hello')\n",
        "code reviewer": "NEEDS_FIX: false\n\n# Code Review\nLGTM",
        "qa engineer": "NEEDS_FIX: false\n\n# Bug Report\nNo bugs",
        "devops engineer": "--- FILE: DEPLOYMENT.md ---\n# Deploy\n--- FILE: Dockerfile ---\nFROM python:3.12\n",
        "technical writer": "--- FILE: README.md ---\n# Project\n--- FILE: docs/api.md ---\n# API\n",
    })


@pytest.mark.asyncio
async def test_full_pipeline_all_agents_with_mocked_provider(async_client):
    with patch("app.orchestrator.create_provider", return_value=make_provider()):
        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "Full Pipeline Test",
                "description": "Test all 8 agents",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        assert response.status_code == 201
        data = response.json()
        pipeline_id = data["pipeline"]["id"]
        assert data["pipeline"]["status"] == "running"

        checkpoints = ["req_engineer", "sw_architect", "qa_engineer"]
        for checkpoint_agent in checkpoints:
            for _ in range(200):
                response = await async_client.get(f"/api/pipelines/{pipeline_id}")
                state = response.json()
                if state["pipeline"]["status"] == "checkpoint" and state["pipeline"]["current_agent"] == checkpoint_agent:
                    break
                await asyncio.sleep(0.05)
            else:
                pytest.fail(f"Pipeline did not reach {checkpoint_agent} checkpoint")

            response = await async_client.post(f"/api/pipelines/{pipeline_id}/approve")
            assert response.status_code == 200

        # Wait for completion
        for _ in range(200):
            response = await async_client.get(f"/api/pipelines/{pipeline_id}")
            state = response.json()
            if state["pipeline"]["status"] == "completed":
                break
            await asyncio.sleep(0.05)
        else:
            pytest.fail("Pipeline did not complete")

        assert state["pipeline"]["status"] == "completed"
        assert state["pipeline"]["overall_progress"] == 100

        # Verify artifacts
        response = await async_client.get(f"/api/pipelines/{pipeline_id}/artifacts")
        assert response.status_code == 200
        artifacts = response.json()["artifacts"]
        paths = {a["path"] for a in artifacts}
        assert "requirements.md" in paths
        assert "plan.md" in paths
        assert "project-plan.md" in paths
        assert "src/main.py" in paths
        assert "review-report.md" in paths
        assert "bug-report.md" in paths
        assert "DEPLOYMENT.md" in paths
        assert "Dockerfile" in paths
        assert "README.md" in paths
        assert "docs/api.md" in paths


@pytest.mark.asyncio
async def test_full_pipeline_needs_fix_loop(async_client):
    fix_iterations = [0]

    class FixLoopProvider(DeterministicProvider):
        async def chat(self, messages, stream=True):
            all_text = " ".join(m.get("content", "") for m in messages)
            if "qa engineer" in all_text.lower():
                if fix_iterations[0] < 2:
                    fix_iterations[0] += 1
                    content = "NEEDS_FIX: true\n\n# Bug Report\nFound bugs"
                else:
                    content = "NEEDS_FIX: false\n\n# Bug Report\nNo bugs"
                yield StreamChunk(content=content, done=True)
                return
            async for chunk in super().chat(messages, stream):
                yield chunk

    with patch("app.orchestrator.create_provider", return_value=FixLoopProvider()):
        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "Fix Loop Test",
                "description": "Test fix loop",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        pipeline_id = response.json()["pipeline"]["id"]

        checkpoints = ["req_engineer", "sw_architect", "qa_engineer"]
        for checkpoint_agent in checkpoints:
            for _ in range(200):
                response = await async_client.get(f"/api/pipelines/{pipeline_id}")
                state = response.json()
                if state["pipeline"]["status"] == "checkpoint" and state["pipeline"]["current_agent"] == checkpoint_agent:
                    break
                await asyncio.sleep(0.05)
            else:
                pytest.fail(f"Pipeline did not reach {checkpoint_agent} checkpoint")

            response = await async_client.post(f"/api/pipelines/{pipeline_id}/approve")
            assert response.status_code == 200

        # Wait for completion
        for _ in range(300):
            response = await async_client.get(f"/api/pipelines/{pipeline_id}")
            state = response.json()
            if state["pipeline"]["status"] == "completed":
                break
            await asyncio.sleep(0.05)
        else:
            pytest.fail("Pipeline did not complete")

        assert state["pipeline"]["status"] == "completed"
        assert fix_iterations[0] == 2


@pytest.mark.asyncio
async def test_checkpoint_blocks_new_pipeline_start(async_client):
    with patch("app.orchestrator.create_provider", return_value=make_provider()):
        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "First Project",
                "description": "Test checkpoint blocks",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        pipeline_id = response.json()["pipeline"]["id"]

        for _ in range(200):
            response = await async_client.get(f"/api/pipelines/{pipeline_id}")
            state = response.json()
            if state["pipeline"]["status"] == "checkpoint":
                break
            await asyncio.sleep(0.05)
        else:
            pytest.fail("Pipeline did not reach checkpoint")

        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "Second Project",
                "description": "Should fail",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        assert response.status_code == 409
        error = response.json()["detail"]
        assert "already running" in error.lower() or "checkpoint" in error.lower()


@pytest.mark.asyncio
async def test_running_blocks_new_pipeline_start(async_client):
    with patch("app.orchestrator.create_provider", return_value=make_provider()):
        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "First Project",
                "description": "Test running blocks",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        assert response.status_code == 201

        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "Second Project",
                "description": "Should fail",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        assert response.status_code == 409
        error = response.json()["detail"]
        assert "already running" in error.lower() or "checkpoint" in error.lower()


@pytest.mark.asyncio
async def test_full_pipeline_fix_loop_exceeds_max_fails(async_client):
    class AlwaysNeedsFixProvider(DeterministicProvider):
        async def chat(self, messages, stream=True):
            all_text = " ".join(m.get("content", "") for m in messages)
            if "code reviewer" in all_text.lower():
                content = "NEEDS_FIX: true\n\n# Code Review\nIssues"
            elif "qa engineer" in all_text.lower():
                content = "NEEDS_FIX: false\n\n# Bug Report\nNo bugs"
            else:
                async for chunk in super().chat(messages, stream):
                    yield chunk
                return
            yield StreamChunk(content=content, done=True)

    with patch("app.orchestrator.create_provider", return_value=AlwaysNeedsFixProvider()):
        response = await async_client.post(
            "/api/pipelines",
            json={
                "project_name": "Fix Loop Fail Test",
                "description": "Test fix loop failure",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        pipeline_id = response.json()["pipeline"]["id"]

        # Approve req checkpoint
        for _ in range(200):
            response = await async_client.get(f"/api/pipelines/{pipeline_id}")
            state = response.json()
            if state["pipeline"]["status"] == "checkpoint":
                break
            await asyncio.sleep(0.05)
        await async_client.post(f"/api/pipelines/{pipeline_id}/approve")

        # Approve arch checkpoint
        for _ in range(200):
            response = await async_client.get(f"/api/pipelines/{pipeline_id}")
            state = response.json()
            if state["pipeline"]["status"] == "checkpoint":
                break
            await asyncio.sleep(0.05)
        await async_client.post(f"/api/pipelines/{pipeline_id}/approve")

        # Wait for failure after code_reviewer fix loop
        for _ in range(400):
            response = await async_client.get(f"/api/pipelines/{pipeline_id}")
            state = response.json()
            if state["pipeline"]["status"] == "failed":
                break
            await asyncio.sleep(0.05)
        else:
            pytest.fail("Pipeline did not fail after max fix iterations")

        assert state["pipeline"]["status"] == "failed"
