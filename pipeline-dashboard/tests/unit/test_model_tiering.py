import app.config as config
from app.config import resolve_agent_model


def test_no_fast_model_means_no_tiering(monkeypatch):
    monkeypatch.setattr(config, "_FAST_MODEL_BY_PROVIDER", {"claude": "", "gemini": ""})
    # Every agent — gate or mechanical — uses the selected model when no fast model set
    for agent in ("sw_architect", "proj_manager", "qa_engineer", "tech_writer"):
        assert resolve_agent_model("claude", "opus", agent) == "opus"


def test_fast_model_only_applies_to_mechanical_agents(monkeypatch):
    monkeypatch.setattr(config, "_FAST_MODEL_BY_PROVIDER", {"claude": "haiku", "gemini": ""})
    # Mechanical phases downtier to the fast model
    assert resolve_agent_model("claude", "opus", "proj_manager") == "haiku"
    assert resolve_agent_model("claude", "opus", "devops_engineer") == "haiku"
    assert resolve_agent_model("claude", "opus", "tech_writer") == "haiku"
    # Gate/judgment phases ALWAYS keep the strong (selected) model — quality guard
    assert resolve_agent_model("claude", "opus", "sw_architect") == "opus"
    assert resolve_agent_model("claude", "opus", "code_reviewer") == "opus"
    assert resolve_agent_model("claude", "opus", "qa_engineer") == "opus"


def test_fast_model_is_provider_specific(monkeypatch):
    monkeypatch.setattr(
        config, "_FAST_MODEL_BY_PROVIDER",
        {"claude": "haiku", "gemini": "gemini-2.5-flash"},
    )
    assert resolve_agent_model("claude", "opus", "tech_writer") == "haiku"
    assert resolve_agent_model("gemini", "gemini-2.5-pro", "tech_writer") == "gemini-2.5-flash"
    # A provider with no fast model configured falls back to the selected model
    assert resolve_agent_model("ollama", "llama3.2", "tech_writer") == "llama3.2"
