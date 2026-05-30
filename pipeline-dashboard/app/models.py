from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncIterator, Callable
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class PipelineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    CHECKPOINT = "checkpoint"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BuildProfile(BaseModel):
    """What to build and what to skip. Presets set sensible defaults; users override
    individual toggles. Gate phases (architect, dev) are always run and not listed here."""
    model_config = ConfigDict(from_attributes=True)

    rigor: str = "standard"          # mvp / small / standard / production (label only)
    code_review: bool = True         # run the code-review phase
    qa: bool = True                  # run the QA phase
    e2e_tests: bool = True           # full UI end-to-end tests (vs smoke only)
    load_test: bool = False          # load/performance testing
    dast: bool = False               # dynamic application security testing
    security_scan: bool = True       # SAST + dependency scanning
    accessibility: bool = True       # accessibility checks
    devops: bool = True              # run the DevOps phase
    docs: bool = True                # run the documentation phase


class PipelineRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    project_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    provider: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    fast_model: str | None = None
    build_profile: BuildProfile = Field(default_factory=BuildProfile)
    status: PipelineStatus = PipelineStatus.IDLE
    current_agent: str | None = None
    overall_progress: int = Field(0, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    checkpoint_artifact_path: str | None = None
    checkpoint_feedback: str | None = None


class AgentRun(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    pipeline_id: UUID
    agent_name: str = Field(..., min_length=1)
    status: AgentStatus = AgentStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int | None = None
    artifact_paths: list[str] = Field(default_factory=list)
    error_message: str | None = None
    log_tail: str | None = None


class SecurityEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    pipeline_id: UUID | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = Field(..., min_length=1)
    detail: str = Field(..., min_length=1)
    command: str | None = None


class PipelineCreate(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    provider: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    fast_model: str | None = None
    build_profile: BuildProfile | None = None


class ProviderInfo(BaseModel):
    name: str
    available: bool
    models: list[str] = Field(default_factory=list)
    error: str | None = None


class ArtifactInfo(BaseModel):
    name: str
    path: str
    size: int
    is_dir: bool
    modified_at: datetime


@dataclass
class StreamChunk:
    role: str = "assistant"
    content: str = ""
    done: bool = False
    error: str | None = None


@dataclass
class AgentContext:
    project_path: str
    provider_name: str
    model: str
    pipeline_id: UUID
    log_callback: Callable[[str], None]
    guardrails: Any = None
    feedback: list[str] = field(default_factory=list)
    build_profile: Any = None


@dataclass
class AgentResult:
    status: str
    artifact_paths: list[str] = field(default_factory=list)
    error_message: str | None = None
    duration_ms: int | None = None
    needs_fix: bool = False
