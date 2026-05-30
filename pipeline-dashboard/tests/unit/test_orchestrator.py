import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4

import aiosqlite

from app.database import init_schema, get_db_path
from app.dao import AgentDAO, PipelineDAO
from app.models import AgentRun, AgentStatus, PipelineRun, PipelineStatus
from app.orchestrator import Orchestrator


@pytest_asyncio.fixture
async def orch_fixtures(monkeypatch, tmp_path):
    db_path = str(tmp_path / "test.db")

    async def override_get_db_path():
        return db_path

    monkeypatch.setattr("app.database.get_db_path", override_get_db_path)

    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = aiosqlite.Row
    await init_schema(conn)
    await conn.close()

    orch = Orchestrator()
    yield {"orch": orch, "pipeline_dao": PipelineDAO(), "agent_dao": AgentDAO()}


@pytest.mark.asyncio
async def test_start_pipeline_transitions_to_running(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(
        project_name="Test",
        description="Desc",
        provider="ollama",
        model="llama3.2",
    )
    created = await orch.start_pipeline(run)
    assert created.status == PipelineStatus.RUNNING
    assert created.current_agent == "req_engineer"


@pytest.mark.asyncio
async def test_single_pipeline_enforcement(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run1 = PipelineRun(project_name="A", description="Desc", provider="ollama", model="llama3.2")
    await orch.start_pipeline(run1)

    run2 = PipelineRun(project_name="B", description="Desc", provider="ollama", model="llama3.2")
    with pytest.raises(RuntimeError, match="already running"):
        await orch.start_pipeline(run2)


@pytest.mark.asyncio
async def test_approve_checkpoint_advances_agent(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    pipeline_dao = orch_fixtures["pipeline_dao"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run = await orch.start_pipeline(run)

    run.status = PipelineStatus.CHECKPOINT
    run.current_agent = "req_engineer"
    await pipeline_dao.update(run)

    updated = await orch.approve_checkpoint(run.id)
    assert updated.status == PipelineStatus.RUNNING
    assert updated.current_agent == "sw_architect"


@pytest.mark.asyncio
async def test_approve_checkpoint_completes_pipeline(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    pipeline_dao = orch_fixtures["pipeline_dao"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run = await orch.start_pipeline(run)

    run.status = PipelineStatus.CHECKPOINT
    run.current_agent = "tech_writer"
    await pipeline_dao.update(run)

    updated = await orch.approve_checkpoint(run.id)
    assert updated.status == PipelineStatus.COMPLETED
    assert updated.overall_progress == 100


@pytest.mark.asyncio
async def test_submit_feedback_rewinds_agent(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    pipeline_dao = orch_fixtures["pipeline_dao"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run = await orch.start_pipeline(run)

    run.status = PipelineStatus.CHECKPOINT
    run.current_agent = "req_engineer"
    await pipeline_dao.update(run)

    updated = await orch.submit_feedback(run.id, "Make it better")
    assert updated.status == PipelineStatus.RUNNING
    assert updated.current_agent == "req_engineer"
    assert updated.checkpoint_feedback == "Make it better"


@pytest.mark.asyncio
async def test_retry_agent_from_failed(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    pipeline_dao = orch_fixtures["pipeline_dao"]
    agent_dao = orch_fixtures["agent_dao"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run = await orch.start_pipeline(run)

    run.status = PipelineStatus.FAILED
    await pipeline_dao.update(run)

    agents = await agent_dao.list_by_pipeline(run.id)
    agent = agents[0]
    agent.status = AgentStatus.FAILED
    agent.error_message = "boom"
    await agent_dao.update(agent)

    updated = await orch.retry_agent(run.id, agent.agent_name)
    assert updated.status == PipelineStatus.RUNNING
    assert updated.current_agent == agent.agent_name

    agent_after = await agent_dao.get(agent.id)
    assert agent_after.status == AgentStatus.PENDING
    assert agent_after.error_message is None


@pytest.mark.asyncio
async def test_on_startup_orphans_marked_failed(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    pipeline_dao = orch_fixtures["pipeline_dao"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run.status = PipelineStatus.RUNNING
    run = await pipeline_dao.create(run)

    await orch.on_startup()

    updated = await pipeline_dao.get(run.id)
    assert updated.status == PipelineStatus.FAILED


@pytest.mark.asyncio
async def test_on_startup_checkpoint_orphans_marked_failed(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    pipeline_dao = orch_fixtures["pipeline_dao"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run.status = PipelineStatus.CHECKPOINT
    run.current_agent = "req_engineer"
    run = await pipeline_dao.create(run)

    await orch.on_startup()

    updated = await pipeline_dao.get(run.id)
    assert updated.status == PipelineStatus.FAILED


@pytest.mark.asyncio
async def test_get_state_returns_pipeline_and_agents(orch_fixtures, monkeypatch, tmp_path):
    orch = orch_fixtures["orch"]
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setattr("app.orchestrator.settings.projects_dir", projects_dir)

    run = PipelineRun(project_name="Test", description="Desc", provider="ollama", model="llama3.2")
    run = await orch.start_pipeline(run)

    state = await orch.get_state(run.id)
    assert "pipeline" in state
    assert "agents" in state
    assert len(state["agents"]) == 8
