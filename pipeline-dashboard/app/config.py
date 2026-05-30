import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///data/pipeline.db"
    projects_dir: Path = Path(os.environ.get("PIPELINE_PROJECTS_DIR") or "projects")
    data_dir: Path = Path("data")
    ollama_base_url: str = "http://localhost:11434"
    claude_cli_path: str = "claude"
    gemini_cli_path: str = "gemini"
    # Curated model lists for CLI providers (no enumeration command exists).
    # Comma-separated; override in .env without touching code.
    claude_models: str = "opus,sonnet,haiku,claude-opus-4-8,claude-sonnet-4-6,claude-haiku-4-5"
    gemini_models: str = "gemini-2.5-pro,gemini-2.5-flash,gemini-2.0-flash,gemini-2.5-flash-lite"
    # Per-agent model tiering (speed). The user's selected model is the "strong" tier
    # used for judgment/gate phases (architect, code review, QA). Mechanical phases can
    # run on a faster model of the SAME provider. Leave empty to disable (all agents use
    # the selected model — no behavior change, no quality risk).
    claude_fast_model: str = ""   # e.g. "haiku"
    gemini_fast_model: str = ""   # e.g. "gemini-2.5-flash"
    guardrails_file: Path = Path("guardrails.json")
    env: str = "dev"
    host: str = "127.0.0.1"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Ignore unknown keys in .env (e.g. PIPELINE_PROJECTS_DIR, which is read
        # directly from os.environ) instead of failing to start.
        extra = "ignore"


settings = Settings()


def _parse_models(raw: str) -> list[str]:
    return [m.strip() for m in raw.split(",") if m.strip()]


CLAUDE_MODELS = _parse_models(settings.claude_models)
GEMINI_MODELS = _parse_models(settings.gemini_models)

# Agents that may run on the faster model tier. The judgment/gate phases —
# sw_architect, code_reviewer, qa_engineer — are deliberately EXCLUDED so quality
# at the critical phases is never traded for speed.
FAST_TIER_AGENTS = {"proj_manager", "devops_engineer", "tech_writer"}

_FAST_MODEL_BY_PROVIDER = {
    "claude": settings.claude_fast_model,
    "gemini": settings.gemini_fast_model,
}


def resolve_agent_model(provider: str, base_model: str, agent_name: str, fast_model: str | None = None) -> str:
    """Return the model an agent should use. Fast-tier agents use the fast model — taken
    from the per-build override if given, else the provider's configured fast model — and
    everything else uses the user's selected (strong) model."""
    if agent_name in FAST_TIER_AGENTS:
        fast = (fast_model or "").strip() or _FAST_MODEL_BY_PROVIDER.get(provider, "")
        if fast:
            return fast
    return base_model


# Build profile presets — what each "project size" runs by default. Users start from one
# of these in the UI / skill, then toggle individual items. Keep in sync with the frontend.
BUILD_PROFILE_PRESETS = {
    "mvp": {
        "rigor": "mvp",
        "code_review": True, "qa": True, "e2e_tests": False, "load_test": False,
        "dast": False, "security_scan": True, "accessibility": False,
        "devops": False, "docs": False,
    },
    "small": {
        "rigor": "small",
        "code_review": True, "qa": True, "e2e_tests": True, "load_test": False,
        "dast": False, "security_scan": True, "accessibility": False,
        "devops": False, "docs": True,
    },
    "standard": {
        "rigor": "standard",
        "code_review": True, "qa": True, "e2e_tests": True, "load_test": False,
        "dast": False, "security_scan": True, "accessibility": True,
        "devops": True, "docs": True,
    },
    "production": {
        "rigor": "production",
        "code_review": True, "qa": True, "e2e_tests": True, "load_test": True,
        "dast": True, "security_scan": True, "accessibility": True,
        "devops": True, "docs": True,
    },
}

VERSION = "0.1.0"

PIPELINE_AGENTS = [
    "req_engineer",
    "sw_architect",
    "proj_manager",
    "sw_developer",
    "code_reviewer",
    "qa_engineer",
    "devops_engineer",
    "tech_writer",
]
