import json
from datetime import datetime, timezone
from uuid import UUID

from app.database import get_db, backup_database
from app.models import AgentRun, AgentStatus, BuildProfile, PipelineRun, PipelineStatus, SecurityEvent


class PipelineDAO:
    async def create(self, run: PipelineRun) -> PipelineRun:
        async with get_db() as conn:
            await conn.execute(
                """
                INSERT INTO pipeline_runs
                (id, project_name, description, provider, model, status, current_agent,
                 overall_progress, created_at, updated_at, completed_at,
                 checkpoint_artifact_path, checkpoint_feedback, fast_model, build_profile)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(run.id), run.project_name, run.description, run.provider,
                    run.model, run.status.value, run.current_agent,
                    run.overall_progress, run.created_at.isoformat(),
                    run.updated_at.isoformat(),
                    run.completed_at.isoformat() if run.completed_at else None,
                    run.checkpoint_artifact_path, run.checkpoint_feedback,
                    run.fast_model, run.build_profile.model_dump_json(),
                ),
            )
            await conn.commit()
        return run

    async def get(self, run_id: UUID) -> PipelineRun | None:
        async with get_db() as conn:
            cursor = await conn.execute(
                "SELECT * FROM pipeline_runs WHERE id = ?", (str(run_id),)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[PipelineRun]:
        async with get_db() as conn:
            cursor = await conn.execute(
                "SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            rows = await cursor.fetchall()
            return [self._row_to_model(r) for r in rows]

    async def update(self, run: PipelineRun) -> PipelineRun:
        run.updated_at = datetime.now(timezone.utc)
        await backup_database()
        async with get_db() as conn:
            await conn.execute(
                """
                UPDATE pipeline_runs SET
                project_name = ?, description = ?, provider = ?, model = ?,
                status = ?, current_agent = ?, overall_progress = ?,
                updated_at = ?, completed_at = ?,
                checkpoint_artifact_path = ?, checkpoint_feedback = ?,
                fast_model = ?, build_profile = ?
                WHERE id = ?
                """,
                (
                    run.project_name, run.description, run.provider, run.model,
                    run.status.value, run.current_agent, run.overall_progress,
                    run.updated_at.isoformat(),
                    run.completed_at.isoformat() if run.completed_at else None,
                    run.checkpoint_artifact_path, run.checkpoint_feedback,
                    run.fast_model, run.build_profile.model_dump_json(),
                    str(run.id),
                ),
            )
            await conn.commit()
        return run

    async def delete(self, run_id: UUID) -> None:
        async with get_db() as conn:
            await conn.execute("DELETE FROM agent_runs WHERE pipeline_id = ?", (str(run_id),))
            await conn.execute("DELETE FROM security_events WHERE pipeline_id = ?", (str(run_id),))
            await conn.execute("DELETE FROM pipeline_runs WHERE id = ?", (str(run_id),))
            await conn.commit()
        import shutil
        from app.config import settings
        project_dir = settings.projects_dir / str(run_id)
        if project_dir.exists():
            shutil.rmtree(project_dir)

    async def get_current(self) -> PipelineRun | None:
        async with get_db() as conn:
            cursor = await conn.execute(
                """
                SELECT * FROM pipeline_runs
                WHERE status IN (?, ?)
                ORDER BY updated_at DESC LIMIT 1
                """,
                (PipelineStatus.RUNNING.value, PipelineStatus.CHECKPOINT.value),
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_model(row)
            cursor = await conn.execute(
                "SELECT * FROM pipeline_runs ORDER BY updated_at DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_model(row)
            return None

    def _row_to_model(self, row) -> PipelineRun:
        data = dict(row)
        data["id"] = UUID(data["id"])
        data["status"] = PipelineStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        else:
            data["completed_at"] = None
        raw_profile = data.get("build_profile")
        data["build_profile"] = (
            BuildProfile.model_validate_json(raw_profile) if raw_profile else BuildProfile()
        )
        return PipelineRun(**data)


class AgentDAO:
    async def create(self, run: AgentRun) -> AgentRun:
        async with get_db() as conn:
            await conn.execute(
                """
                INSERT INTO agent_runs
                (id, pipeline_id, agent_name, status, started_at, completed_at,
                 duration_ms, artifact_paths, error_message, log_tail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(run.id), str(run.pipeline_id), run.agent_name,
                    run.status.value,
                    run.started_at.isoformat() if run.started_at else None,
                    run.completed_at.isoformat() if run.completed_at else None,
                    run.duration_ms,
                    json.dumps(run.artifact_paths),
                    run.error_message, run.log_tail,
                ),
            )
            await conn.commit()
        return run

    async def get(self, run_id: UUID) -> AgentRun | None:
        async with get_db() as conn:
            cursor = await conn.execute(
                "SELECT * FROM agent_runs WHERE id = ?", (str(run_id),)
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_model(row)

    async def list_by_pipeline(self, pipeline_id: UUID) -> list[AgentRun]:
        async with get_db() as conn:
            cursor = await conn.execute(
                "SELECT * FROM agent_runs WHERE pipeline_id = ? ORDER BY started_at ASC",
                (str(pipeline_id),),
            )
            rows = await cursor.fetchall()
            return [self._row_to_model(r) for r in rows]

    async def update(self, run: AgentRun) -> AgentRun:
        async with get_db() as conn:
            await conn.execute(
                """
                UPDATE agent_runs SET
                agent_name = ?, status = ?, started_at = ?, completed_at = ?,
                duration_ms = ?, artifact_paths = ?, error_message = ?, log_tail = ?
                WHERE id = ?
                """,
                (
                    run.agent_name, run.status.value,
                    run.started_at.isoformat() if run.started_at else None,
                    run.completed_at.isoformat() if run.completed_at else None,
                    run.duration_ms, json.dumps(run.artifact_paths),
                    run.error_message, run.log_tail,
                    str(run.id),
                ),
            )
            await conn.commit()
        return run

    async def delete(self, run_id: UUID) -> None:
        async with get_db() as conn:
            await conn.execute("DELETE FROM agent_runs WHERE id = ?", (str(run_id),))
            await conn.commit()

    def _row_to_model(self, row) -> AgentRun:
        data = dict(row)
        data["id"] = UUID(data["id"])
        data["pipeline_id"] = UUID(data["pipeline_id"])
        data["status"] = AgentStatus(data["status"])
        import json
        data["artifact_paths"] = json.loads(data.get("artifact_paths", "[]"))
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        else:
            data["started_at"] = None
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        else:
            data["completed_at"] = None
        return AgentRun(**data)


class SecurityEventDAO:
    async def create(self, event: SecurityEvent) -> SecurityEvent:
        async with get_db() as conn:
            await conn.execute(
                """
                INSERT INTO security_events
                (id, pipeline_id, timestamp, event_type, detail, command)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event.id), str(event.pipeline_id) if event.pipeline_id else None,
                    event.timestamp.isoformat(), event.event_type,
                    event.detail, event.command,
                ),
            )
            await conn.commit()
        return event

    async def list_recent(self, limit: int = 100) -> list[SecurityEvent]:
        async with get_db() as conn:
            cursor = await conn.execute(
                "SELECT * FROM security_events ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_model(r) for r in rows]

    def _row_to_model(self, row) -> SecurityEvent:
        data = dict(row)
        data["id"] = UUID(data["id"])
        if data.get("pipeline_id"):
            data["pipeline_id"] = UUID(data["pipeline_id"])
        else:
            data["pipeline_id"] = None
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return SecurityEvent(**data)
