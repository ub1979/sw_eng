import pytest
from pathlib import Path
from unittest.mock import AsyncMock

from app.agents.base import BaseAgent
from app.agents.req_engineer import ReqEngineer
from app.agents.sw_architect import SwArchitect
from app.agents.proj_manager import ProjManager
from app.agents.sw_developer import SwDeveloper
from app.agents.code_reviewer import CodeReviewer
from app.agents.qa_engineer import QaEngineer
from app.agents.devops_engineer import DevOpsEngineer
from app.agents.tech_writer import TechWriter
from app.models import AgentContext, AgentResult, StreamChunk
from app.providers import LLMProvider


class MockProvider(LLMProvider):
    def __init__(self, content: str = ""):
        self._content = content

    async def chat(self, messages, stream=True):
        yield StreamChunk(content=self._content, done=True)

    async def list_models(self):
        return []

    async def health_check(self):
        return {"available": True, "models": [], "error": None}


def make_ctx(tmp_path, feedback=None):
    return AgentContext(
        project_path=str(tmp_path / "project"),
        provider_name="mock",
        model="mock",
        pipeline_id=None,
        log_callback=lambda line: None,
        feedback=feedback or [],
    )


@pytest.mark.asyncio
async def test_req_engineer_writes_requirements(tmp_path):
    ctx = make_ctx(tmp_path)
    provider = MockProvider(content="# Requirements\n\nTest req")
    result = await ReqEngineer().run(ctx, provider)
    assert result.status == "completed"
    assert any("requirements.md" in p for p in result.artifact_paths)
    assert "# Requirements" in Path(result.artifact_paths[0]).read_text()


@pytest.mark.asyncio
async def test_sw_architect_reads_requirements_and_writes_plan(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "requirements.md").write_text("# Requirements")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(content="# Architecture\n\nTech stack: Python")
    result = await SwArchitect().run(ctx, provider)
    assert result.status == "completed"
    assert any("plan.md" in p for p in result.artifact_paths)


@pytest.mark.asyncio
async def test_proj_manager_reads_plan_and_writes_project_plan(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "plan.md").write_text("# Architecture")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(content="# Project Plan\n\nEpic 1")
    result = await ProjManager().run(ctx, provider)
    assert result.status == "completed"
    assert any("project-plan.md" in p for p in result.artifact_paths)


@pytest.mark.asyncio
async def test_sw_developer_reads_artifacts_and_writes_src(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "requirements.md").write_text("# Requirements")
    (project_dir / "plan.md").write_text("# Architecture")
    (project_dir / "project-plan.md").write_text("# Project Plan")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(
        content="--- FILE: src/main.py ---\nprint('hello')\n"
    )
    result = await SwDeveloper().run(ctx, provider)
    assert result.status == "completed"
    assert any("src/main.py" in p for p in result.artifact_paths)


@pytest.mark.asyncio
async def test_code_reviewer_detects_needs_fix(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "src/main.py").write_text("print('hello')")
    (project_dir / "plan.md").write_text("# Architecture")
    (project_dir / "project-plan.md").write_text("# Project Plan")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(content="NEEDS_FIX: true\n\n# Review\nIssues found")
    result = await CodeReviewer().run(ctx, provider)
    assert result.status == "completed"
    assert result.needs_fix is True
    assert any("review-report.md" in p for p in result.artifact_paths)


@pytest.mark.asyncio
async def test_code_reviewer_no_fix_needed(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "src/main.py").write_text("print('hello')")
    (project_dir / "plan.md").write_text("# Architecture")
    (project_dir / "project-plan.md").write_text("# Project Plan")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(content="NEEDS_FIX: false\n\n# Review\nLGTM")
    result = await CodeReviewer().run(ctx, provider)
    assert result.status == "completed"
    assert result.needs_fix is False


@pytest.mark.asyncio
async def test_qa_engineer_detects_needs_fix(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "src/main.py").write_text("print('hello')")
    (project_dir / "requirements.md").write_text("# Requirements")
    (project_dir / "project-plan.md").write_text("# Project Plan")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(content="NEEDS_FIX: true\n\n# Bug Report\nBugs found")
    result = await QaEngineer().run(ctx, provider)
    assert result.status == "completed"
    assert result.needs_fix is True
    assert any("bug-report.md" in p for p in result.artifact_paths)


@pytest.mark.asyncio
async def test_devops_engineer_writes_deployment_files(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "plan.md").write_text("# Architecture")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(
        content="--- FILE: DEPLOYMENT.md ---\n# Deploy\n--- FILE: Dockerfile ---\nFROM python\n"
    )
    result = await DevOpsEngineer().run(ctx, provider)
    assert result.status == "completed"
    assert any("DEPLOYMENT.md" in p for p in result.artifact_paths)
    assert any("Dockerfile" in p for p in result.artifact_paths)


@pytest.mark.asyncio
async def test_tech_writer_writes_docs(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "requirements.md").write_text("# Requirements")
    ctx = make_ctx(tmp_path)
    provider = MockProvider(
        content="--- FILE: README.md ---\n# Project\n--- FILE: docs/api.md ---\n# API\n"
    )
    result = await TechWriter().run(ctx, provider)
    assert result.status == "completed"
    assert any("README.md" in p for p in result.artifact_paths)
    assert any("docs/api.md" in p for p in result.artifact_paths)


class DummyAgent(BaseAgent):
    name = "dummy"

    def system_prompt(self) -> str:
        return ""

    async def run(self, ctx, provider) -> AgentResult:
        return AgentResult(status="completed")


class TestBaseAgent:
    def test_parse_multiple_files_with_delimiters(self):
        content = "--- FILE: src/a.py ---\nprint(1)\n--- FILE: src/b.py ---\nprint(2)\n"
        agent = DummyAgent()
        files = agent.parse_multiple_files(content)
        assert files == {"src/a.py": "print(1)", "src/b.py": "print(2)"}

    def test_parse_multiple_files_without_delimiters(self):
        content = "# Just markdown"
        agent = DummyAgent()
        files = agent.parse_multiple_files(content)
        assert files == {"output.md": "# Just markdown"}

    def test_write_and_read_artifact(self, tmp_path):
        agent = DummyAgent()
        path = agent.write_artifact(tmp_path, "test.txt", "hello")
        assert path.exists()
        assert agent.read_artifact(tmp_path, "test.txt") == "hello"

    def test_read_all_artifacts(self, tmp_path):
        agent = DummyAgent()
        agent.write_artifact(tmp_path, "a.py", "x")
        agent.write_artifact(tmp_path, "b.md", "y")
        files = agent.read_all_artifacts(tmp_path, extensions=[".py"])
        assert "a.py" in files
        assert "b.md" not in files
