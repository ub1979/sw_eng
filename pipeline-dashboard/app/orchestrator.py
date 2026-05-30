import asyncio
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from app.config import PIPELINE_AGENTS, resolve_agent_model, settings
from app.dao import AgentDAO, PipelineDAO
from app.models import AgentContext, AgentResult, AgentRun, AgentStatus, PipelineRun, PipelineStatus
from app.providers import create_provider
from app.routers.sse import sse_manager


class PipelineState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    CHECKPOINT = "checkpoint"
    COMPLETED = "completed"
    FAILED = "failed"


_AGENT_CHECKPOINTS = {
    "req_engineer",
    "sw_architect",
    "qa_engineer",
}

_AGENT_TIMEOUT_SECONDS = 30 * 60
_RETRY_BACKOFFS = [2, 4, 8]
_MAX_FIX_ITERATIONS = 3

# devops + docs are independent consumers of the finished code — run them concurrently
# as the final stage. Order matches their position at the tail of PIPELINE_AGENTS.
_TERMINAL_PARALLEL = ("devops_engineer", "tech_writer")

# Optional phases the build profile can skip. Everything else (req, architect, planner,
# developer) is mandatory and always runs. Each value reads the matching profile toggle.
_OPTIONAL_AGENTS = {
    "code_reviewer": lambda p: p.code_review,
    "qa_engineer": lambda p: p.qa,
    "devops_engineer": lambda p: p.devops,
    "tech_writer": lambda p: p.docs,
}


def _effective_agents(profile) -> list[str]:
    """The agent sequence for this run after applying the build profile's skips."""
    return [
        a for a in PIPELINE_AGENTS
        if a not in _OPTIONAL_AGENTS or _OPTIONAL_AGENTS[a](profile)
    ]


class Orchestrator:
    def __init__(self) -> None:
        self.pipeline_dao = PipelineDAO()
        self.agent_dao = AgentDAO()
        self._lock = asyncio.Lock()
        self._fix_iterations: dict[UUID, int] = {}

    async def start_pipeline(self, run: PipelineRun) -> PipelineRun:
        async with self._lock:
            current = await self.pipeline_dao.get_current()
            if current and current.status in (PipelineStatus.RUNNING, PipelineStatus.CHECKPOINT):
                raise RuntimeError("A pipeline is already running or paused at a checkpoint.")

            effective = _effective_agents(run.build_profile)
            run.status = PipelineStatus.RUNNING
            run.current_agent = effective[0]
            run = await self.pipeline_dao.create(run)

            project_dir = settings.projects_dir / str(run.id)
            project_dir.mkdir(parents=True, exist_ok=True)

            for agent_name in effective:
                agent = AgentRun(
                    pipeline_id=run.id,
                    agent_name=agent_name,
                    status=AgentStatus.PENDING,
                )
                await self.agent_dao.create(agent)

            run = await self._transition(run, PipelineStatus.RUNNING, effective[0])

        asyncio.create_task(self._run_pipeline(run.id))
        return run

    async def _run_pipeline(self, run_id: UUID) -> None:
        run = await self.pipeline_dao.get(run_id)
        if run is None:
            return

        while run.status == PipelineStatus.RUNNING and run.current_agent:
            agent_name = run.current_agent

            # Terminal stage: devops + docs are independent — run them concurrently,
            # then finish. Scope to whichever are enabled by the build profile.
            terminal_group = [a for a in _TERMINAL_PARALLEL if a in _effective_agents(run.build_profile)]
            if terminal_group and agent_name == terminal_group[0]:
                results = await asyncio.gather(
                    *[self.run_agent(run_id, a) for a in terminal_group],
                    return_exceptions=True,
                )
                errors = [r for r in results if isinstance(r, Exception)]
                run = await self.pipeline_dao.get(run_id)
                if run is None:
                    return
                if errors:
                    run = await self._transition(run, PipelineStatus.FAILED, None)
                    await sse_manager.publish(run_id, "error", {"detail": str(errors[0])})
                    return
                run = await self._transition(run, PipelineStatus.COMPLETED, None)
                await sse_manager.publish(run_id, "complete", run.model_dump(mode="json"))
                return

            try:
                result = await self.run_agent(run_id, agent_name)
            except Exception as exc:
                run = await self.pipeline_dao.get(run_id)
                if run is None:
                    return
                run.status = PipelineStatus.FAILED
                run = await self.pipeline_dao.update(run)
                await sse_manager.publish(run_id, "error", {"detail": str(exc)})
                return

            run = await self.pipeline_dao.get(run_id)
            if run is None:
                return

            if result.needs_fix and agent_name in ("code_reviewer", "qa_engineer"):
                iteration = self._fix_iterations.get(run_id, 0) + 1
                if iteration > _MAX_FIX_ITERATIONS:
                    run = await self._transition(run, PipelineStatus.FAILED, None)
                    await sse_manager.publish(run_id, "error", {
                        "detail": f"Fix loop exceeded {_MAX_FIX_ITERATIONS} iterations after {agent_name}.",
                    })
                    return
                self._fix_iterations[run_id] = iteration
                run = await self._transition(run, PipelineStatus.RUNNING, "sw_developer")
                await sse_manager.publish(run_id, "log", {
                    "agent": "orchestrator",
                    "line": f"[{agent_name}] requested fixes. Looping back to sw_developer (iteration {iteration}).",
                })
                continue

            if agent_name in _AGENT_CHECKPOINTS:
                run = await self.pipeline_dao.get(run_id)
                if run:
                    artifact_path = result.artifact_paths[0] if result.artifact_paths else None
                    run.checkpoint_artifact_path = artifact_path
                    run.checkpoint_feedback = None
                    run = await self._transition(run, PipelineStatus.CHECKPOINT, agent_name)
                    await sse_manager.publish(run_id, "checkpoint", {
                        "agent": agent_name,
                        "artifact_path": artifact_path,
                        "pipeline": run.model_dump(mode="json"),
                    })
                return

            next_agent = self._next_agent(run)
            if next_agent is None:
                run = await self._transition(run, PipelineStatus.COMPLETED, None)
                await sse_manager.publish(run_id, "complete", run.model_dump(mode="json"))
            else:
                run = await self._transition(run, PipelineStatus.RUNNING, next_agent)

    async def run_agent(self, pipeline_id: UUID, agent_name: str) -> AgentResult:
        run = await self.pipeline_dao.get(pipeline_id)
        if run is None:
            raise RuntimeError(f"Pipeline {pipeline_id} not found")

        agents = await self.agent_dao.list_by_pipeline(pipeline_id)
        agent = next((a for a in agents if a.agent_name == agent_name), None)
        if agent is None:
            raise RuntimeError(f"Agent {agent_name} not found for pipeline {pipeline_id}")

        agent.status = AgentStatus.RUNNING
        agent.started_at = datetime.now(timezone.utc)
        agent.error_message = None
        await self.agent_dao.update(agent)

        run.current_agent = agent_name
        await self.pipeline_dao.update(run)

        await sse_manager.publish(pipeline_id, "agent_start", {
            "agent": agent_name,
            "pipeline": run.model_dump(mode="json"),
        })

        agent_model = resolve_agent_model(run.provider, run.model, agent_name, run.fast_model)
        provider = create_provider(run.provider, agent_model)
        project_dir = settings.projects_dir / str(run.id)

        log_lines: list[str] = []

        def log_callback(line: str) -> None:
            log_lines.append(line)
            agent.log_tail = "\n".join(log_lines[-500:])
            asyncio.create_task(self.agent_dao.update(agent))
            asyncio.create_task(sse_manager.publish(pipeline_id, "log", {
                "agent": agent_name,
                "line": line,
            }))

        ctx = AgentContext(
            project_path=str(project_dir),
            provider_name=run.provider,
            model=agent_model,
            pipeline_id=pipeline_id,
            log_callback=log_callback,
            feedback=([run.checkpoint_feedback] if run.checkpoint_feedback else []),
            build_profile=run.build_profile,
        )

        last_error: Exception | None = None
        for attempt in range(len(_RETRY_BACKOFFS) + 1):
            try:
                start_ms = int(time.time() * 1000)
                coro = self._invoke_agent(agent_name, ctx, provider)
                result = await asyncio.wait_for(coro, timeout=_AGENT_TIMEOUT_SECONDS)
                duration_ms = int(time.time() * 1000) - start_ms

                agent.status = AgentStatus.COMPLETED
                agent.completed_at = datetime.now(timezone.utc)
                agent.duration_ms = duration_ms
                agent.artifact_paths = result.artifact_paths
                await self.agent_dao.update(agent)

                return result
            except Exception as exc:
                last_error = exc
                if attempt < len(_RETRY_BACKOFFS):
                    delay = _RETRY_BACKOFFS[attempt]
                    log_callback(f"[retry] Agent {agent_name} failed (attempt {attempt + 1}), retrying in {delay}s: {exc}")
                    await asyncio.sleep(delay)

        agent.status = AgentStatus.FAILED
        agent.completed_at = datetime.now(timezone.utc)
        agent.error_message = str(last_error) if last_error else "Unknown error"
        await self.agent_dao.update(agent)

        if last_error:
            raise last_error
        raise RuntimeError(f"Agent {agent_name} failed after all retries")

    async def _invoke_agent(self, agent_name: str, ctx: AgentContext, provider: Any) -> AgentResult:
        if agent_name == "req_engineer":
            from app.agents.req_engineer import run as agent_run
        elif agent_name == "sw_architect":
            from app.agents.sw_architect import run as agent_run
        elif agent_name == "proj_manager":
            from app.agents.proj_manager import run as agent_run
        elif agent_name == "sw_developer":
            from app.agents.sw_developer import run as agent_run
        elif agent_name == "code_reviewer":
            from app.agents.code_reviewer import run as agent_run
        elif agent_name == "qa_engineer":
            from app.agents.qa_engineer import run as agent_run
        elif agent_name == "devops_engineer":
            from app.agents.devops_engineer import run as agent_run
        elif agent_name == "tech_writer":
            from app.agents.tech_writer import run as agent_run
        else:
            raise RuntimeError(f"Unknown agent: {agent_name}")

        ctx.log_callback(f"[{agent_name}] Starting...")
        result = await agent_run(ctx, provider)
        ctx.log_callback(f"[{agent_name}] Finished with status={result.status}")
        return result

    async def approve_checkpoint(self, run_id: UUID) -> PipelineRun:
        async with self._lock:
            run = await self._get_or_raise(run_id)
            if run.status != PipelineStatus.CHECKPOINT:
                raise RuntimeError("Pipeline is not at a checkpoint.")

            run.checkpoint_feedback = None
            next_agent = self._next_agent(run)
            if next_agent is None:
                run = await self._transition(run, PipelineStatus.COMPLETED, None)
                await sse_manager.publish(run_id, "complete", run.model_dump(mode="json"))
            else:
                run = await self._transition(run, PipelineStatus.RUNNING, next_agent)
                asyncio.create_task(self._run_pipeline(run_id))
        return run

    async def submit_feedback(self, run_id: UUID, feedback: str) -> PipelineRun:
        async with self._lock:
            run = await self._get_or_raise(run_id)
            if run.status != PipelineStatus.CHECKPOINT:
                raise RuntimeError("Pipeline is not at a checkpoint.")

            run.checkpoint_feedback = feedback
            run = await self.pipeline_dao.update(run)
            run = await self._transition(run, PipelineStatus.RUNNING, run.current_agent)
            asyncio.create_task(self._run_pipeline(run_id))
        return run

    async def retry_agent(self, run_id: UUID, agent_name: str) -> PipelineRun:
        async with self._lock:
            run = await self._get_or_raise(run_id)
            if run.status != PipelineStatus.FAILED:
                raise RuntimeError("Pipeline is not in failed state.")

            agents = await self.agent_dao.list_by_pipeline(run_id)
            agent = next((a for a in agents if a.agent_name == agent_name), None)
            if agent is None:
                raise RuntimeError(f"Agent {agent_name} not found.")

            agent.status = AgentStatus.PENDING
            agent.error_message = None
            agent.completed_at = None
            agent.duration_ms = None
            await self.agent_dao.update(agent)

            run = await self._transition(run, PipelineStatus.RUNNING, agent_name)
            asyncio.create_task(self._run_pipeline(run_id))
        return run

    async def get_state(self, run_id: UUID) -> dict[str, Any]:
        run = await self._get_or_raise(run_id)
        agents = await self.agent_dao.list_by_pipeline(run_id)
        return {
            "pipeline": run.model_dump(mode="json"),
            "agents": [a.model_dump(mode="json") for a in agents],
        }

    async def on_startup(self) -> None:
        runs = await self.pipeline_dao.list_all(limit=1000)
        orphaned = [
            r for r in runs
            if r.status in (PipelineStatus.RUNNING, PipelineStatus.CHECKPOINT)
        ]
        for run in orphaned:
            run.status = PipelineStatus.FAILED
            error_msg = "Pipeline was orphaned (backend restarted while running or checkpoint was left open)."
            await self.pipeline_dao.update(run)
            await sse_manager.publish(run.id, "error", {
                "detail": error_msg,
                "suggestion": "You can retry the failed agent or start a new pipeline.",
            })

    async def _transition(self, run: PipelineRun, status: PipelineStatus, current_agent: str | None) -> PipelineRun:
        run.status = status
        run.current_agent = current_agent
        if status == PipelineStatus.COMPLETED:
            run.overall_progress = 100
            run.completed_at = datetime.now(timezone.utc)
        elif status == PipelineStatus.RUNNING and current_agent:
            effective = _effective_agents(run.build_profile)
            idx = effective.index(current_agent) if current_agent in effective else 0
            run.overall_progress = int((idx / len(effective)) * 100) if effective else 0
        await self.pipeline_dao.update(run)
        return run

    async def _get_or_raise(self, run_id: UUID) -> PipelineRun:
        run = await self.pipeline_dao.get(run_id)
        if run is None:
            raise RuntimeError(f"Pipeline {run_id} not found.")
        return run

    def _next_agent(self, run: PipelineRun) -> str | None:
        effective = _effective_agents(run.build_profile)
        current = run.current_agent
        if current is None:
            return effective[0] if effective else None
        try:
            idx = effective.index(current)
        except ValueError:
            return None
        return effective[idx + 1] if idx + 1 < len(effective) else None


orchestrator = Orchestrator()
