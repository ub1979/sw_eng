import asyncio
import json
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import EventSourceResponse
from fastapi.sse import format_sse_event

from app.dao import AgentDAO, PipelineDAO
from app.models import PipelineStatus

router = APIRouter(prefix="/api")

_pipeline_dao = PipelineDAO()
_agent_dao = AgentDAO()

_HEARTBEAT_INTERVAL = 30.0


class SSEManager:
    def __init__(self) -> None:
        self._queues: dict[UUID, list[asyncio.Queue[bytes]]] = {}

    def _get_queues(self, run_id: UUID) -> list[asyncio.Queue[bytes]]:
        return self._queues.setdefault(run_id, [])

    def connect(self, run_id: UUID) -> asyncio.Queue[bytes]:
        queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=1000)
        self._get_queues(run_id).append(queue)
        return queue

    def disconnect(self, run_id: UUID, queue: asyncio.Queue[bytes]) -> None:
        queues = self._get_queues(run_id)
        if queue in queues:
            queues.remove(queue)
        if not queues and run_id in self._queues:
            del self._queues[run_id]

    async def publish(self, run_id: UUID, event: str, data: dict[str, Any]) -> None:
        queues = self._get_queues(run_id)
        payload = format_sse_event(event=event, data_str=json.dumps(data))
        for queue in queues:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                pass


sse_manager = SSEManager()


async def event_generator(run_id: UUID):
    queue = sse_manager.connect(run_id)
    try:
        run = await _pipeline_dao.get(run_id)
        if run is None:
            yield format_sse_event(event="error", data_str=json.dumps({"detail": "Pipeline not found"}))
            return

        agents = await _agent_dao.list_by_pipeline(run_id)
        state = {
            "pipeline": run.model_dump(mode="json"),
            "agents": [a.model_dump(mode="json") for a in agents],
        }
        yield format_sse_event(event="sync", data_str=json.dumps(state))

        while True:
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=_HEARTBEAT_INTERVAL)
                yield payload
            except asyncio.TimeoutError:
                yield format_sse_event(
                    event="ping",
                    data_str=json.dumps({"ts": str(asyncio.get_event_loop().time())}),
                )

                run = await _pipeline_dao.get(run_id)
                if run and run.status in (PipelineStatus.COMPLETED, PipelineStatus.FAILED):
                    agents = await _agent_dao.list_by_pipeline(run_id)
                    yield format_sse_event(
                        event="sync",
                        data_str=json.dumps({
                            "pipeline": run.model_dump(mode="json"),
                            "agents": [a.model_dump(mode="json") for a in agents],
                        }),
                    )
                    return
    except asyncio.CancelledError:
        return
    finally:
        sse_manager.disconnect(run_id, queue)


@router.get("/pipelines/{run_id}/events")
async def pipeline_events(run_id: UUID) -> EventSourceResponse:
    return EventSourceResponse(event_generator(run_id))
