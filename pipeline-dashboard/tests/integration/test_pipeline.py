import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock, patch
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.database import get_db_path


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

    import asyncio
    from app.database import init_database
    await init_database()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    if db_path.exists():
        db_path.unlink()


@pytest.mark.asyncio
async def test_full_pipeline_start_checkpoint_approve(async_client):
    async def mock_agent_run(ctx, provider):
        ctx.log_callback("Mock agent done")
        from app.models import AgentResult
        return AgentResult(status="completed", artifact_paths=["requirements.md"])

    with patch("app.agents.req_engineer.run", side_effect=mock_agent_run):
        with patch("app.orchestrator.create_provider") as mock_provider_factory:
            mock_provider = AsyncMock()
            mock_provider_factory.return_value = mock_provider

            response = await async_client.post(
                "/api/pipelines",
                json={
                    "project_name": "Test Project",
                    "description": "A test description",
                    "provider": "ollama",
                    "model": "llama3.2",
                },
            )
            assert response.status_code == 201
            data = response.json()
            pipeline_id = data["pipeline"]["id"]
            assert data["pipeline"]["status"] == "running"

            import asyncio
            for _ in range(50):
                response = await async_client.get(f"/api/pipelines/{pipeline_id}")
                state = response.json()
                if state["pipeline"]["status"] == "checkpoint":
                    break
                await asyncio.sleep(0.05)
            else:
                pytest.fail("Pipeline did not reach checkpoint")

            assert state["pipeline"]["status"] == "checkpoint"
            assert state["pipeline"]["current_agent"] == "req_engineer"

            response = await async_client.post(f"/api/pipelines/{pipeline_id}/approve")
            assert response.status_code == 200
            data = response.json()
            assert data["pipeline"]["status"] == "running"
            assert data["pipeline"]["current_agent"] == "sw_architect"


@pytest.mark.asyncio
async def test_pipeline_feedback_rewinds_agent(async_client):
    async def mock_agent_run(ctx, provider):
        ctx.log_callback("Mock agent done")
        from app.models import AgentResult
        return AgentResult(status="completed", artifact_paths=["requirements.md"])

    with patch("app.agents.req_engineer.run", side_effect=mock_agent_run):
        with patch("app.orchestrator.create_provider") as mock_provider_factory:
            mock_provider = AsyncMock()
            mock_provider_factory.return_value = mock_provider

            response = await async_client.post(
                "/api/pipelines",
                json={
                    "project_name": "Feedback Test",
                    "description": "Test feedback",
                    "provider": "ollama",
                    "model": "llama3.2",
                },
            )
            pipeline_id = response.json()["pipeline"]["id"]

            import asyncio
            for _ in range(50):
                response = await async_client.get(f"/api/pipelines/{pipeline_id}")
                state = response.json()
                if state["pipeline"]["status"] == "checkpoint":
                    break
                await asyncio.sleep(0.05)
            else:
                pytest.fail("Pipeline did not reach checkpoint")

            response = await async_client.post(
                f"/api/pipelines/{pipeline_id}/feedback",
                json={"feedback": "Add more detail"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["pipeline"]["status"] == "running"
            assert data["pipeline"]["current_agent"] == "req_engineer"
            assert data["pipeline"]["checkpoint_feedback"] == "Add more detail"


@pytest.mark.asyncio
async def test_pipeline_retry_failed_agent(async_client):
    async def mock_agent_run(ctx, provider):
        ctx.log_callback("Mock agent done")
        from app.models import AgentResult
        return AgentResult(status="completed", artifact_paths=["requirements.md"])

    with patch("app.agents.req_engineer.run", side_effect=mock_agent_run):
        with patch("app.orchestrator.create_provider") as mock_provider_factory:
            mock_provider = AsyncMock()
            mock_provider_factory.return_value = mock_provider

            response = await async_client.post(
                "/api/pipelines",
                json={
                    "project_name": "Retry Test",
                    "description": "Test retry",
                    "provider": "ollama",
                    "model": "llama3.2",
                },
            )
            pipeline_id = response.json()["pipeline"]["id"]

            import asyncio
            for _ in range(50):
                response = await async_client.get(f"/api/pipelines/{pipeline_id}")
                state = response.json()
                if state["pipeline"]["status"] == "checkpoint":
                    break
                await asyncio.sleep(0.05)
            else:
                pytest.fail("Pipeline did not reach checkpoint")

            # Manually fail the pipeline to test retry
            from app.dao import PipelineDAO
            from app.models import PipelineStatus
            pdao = PipelineDAO()
            run = await pdao.get(pipeline_id)
            run.status = PipelineStatus.FAILED
            await pdao.update(run)

            response = await async_client.post(
                f"/api/pipelines/{pipeline_id}/retry",
                json={"agent": "req_engineer"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["pipeline"]["status"] == "running"
