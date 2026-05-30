import pytest
import pytest_asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import aiosqlite

from app.database import init_schema, get_db_path
from app.dao import AgentDAO, PipelineDAO, SecurityEventDAO
from app.models import AgentRun, AgentStatus, PipelineRun, PipelineStatus, SecurityEvent


@pytest_asyncio.fixture
async def dao_fixtures(monkeypatch, tmp_path):
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

    yield {
        "pipeline_dao": PipelineDAO(),
        "agent_dao": AgentDAO(),
        "security_dao": SecurityEventDAO(),
    }


@pytest.mark.asyncio
async def test_pipeline_crud(dao_fixtures):
    pipeline_dao = dao_fixtures["pipeline_dao"]
    run = PipelineRun(
        project_name="Test",
        description="Desc",
        provider="ollama",
        model="llama3.2",
    )
    created = await pipeline_dao.create(run)
    fetched = await pipeline_dao.get(created.id)
    assert fetched is not None
    assert fetched.project_name == "Test"

    fetched.project_name = "Updated"
    updated = await pipeline_dao.update(fetched)
    assert updated.project_name == "Updated"

    all_runs = await pipeline_dao.list_all()
    assert len(all_runs) == 1

    await pipeline_dao.delete(created.id)
    assert await pipeline_dao.get(created.id) is None


@pytest.mark.asyncio
async def test_agent_crud(dao_fixtures):
    pipeline_dao = dao_fixtures["pipeline_dao"]
    agent_dao = dao_fixtures["agent_dao"]
    run = PipelineRun(
        project_name="Test",
        description="Desc",
        provider="ollama",
        model="llama3.2",
    )
    created = await pipeline_dao.create(run)
    agent = AgentRun(
        pipeline_id=created.id,
        agent_name="req_engineer",
        status=AgentStatus.RUNNING,
    )
    agent_created = await agent_dao.create(agent)
    fetched = await agent_dao.get(agent_created.id)
    assert fetched is not None
    assert fetched.agent_name == "req_engineer"

    agents = await agent_dao.list_by_pipeline(created.id)
    assert len(agents) == 1


@pytest.mark.asyncio
async def test_security_event_crud(dao_fixtures):
    security_dao = dao_fixtures["security_dao"]
    event = SecurityEvent(
        event_type="blocked_command",
        detail="sudo was blocked",
        command="sudo apt update",
    )
    created = await security_dao.create(event)
    assert created.event_type == "blocked_command"
    recent = await security_dao.list_recent()
    assert len(recent) == 1


@pytest.mark.asyncio
async def test_backup_on_update(dao_fixtures):
    pipeline_dao = dao_fixtures["pipeline_dao"]
    run = PipelineRun(
        project_name="BackupTest",
        description="Desc",
        provider="ollama",
        model="llama3.2",
    )
    created = await pipeline_dao.create(run)
    created.project_name = "UpdatedForBackup"
    await pipeline_dao.update(created)
    from app.database import get_db_path
    db_path = await get_db_path()
    backup_dir = Path(db_path).parent / "backups"
    assert backup_dir.exists()
    backups = list(backup_dir.glob("pipeline_*.db"))
    assert len(backups) >= 1
