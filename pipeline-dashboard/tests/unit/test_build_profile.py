from app.config import BUILD_PROFILE_PRESETS
from app.models import BuildProfile
from app.orchestrator import _effective_agents


def test_standard_profile_runs_all_agents():
    eff = _effective_agents(BuildProfile())  # default = standard
    assert eff == [
        "req_engineer", "sw_architect", "proj_manager", "sw_developer",
        "code_reviewer", "qa_engineer", "devops_engineer", "tech_writer",
    ]


def test_mvp_profile_skips_devops_and_docs():
    profile = BuildProfile(**BUILD_PROFILE_PRESETS["mvp"])
    eff = _effective_agents(profile)
    assert "devops_engineer" not in eff
    assert "tech_writer" not in eff
    # Core build + gates always remain
    for required in ("req_engineer", "sw_architect", "proj_manager", "sw_developer", "code_reviewer", "qa_engineer"):
        assert required in eff


def test_skipping_optional_agents_keeps_mandatory_ones():
    profile = BuildProfile(code_review=False, qa=False, devops=False, docs=False)
    eff = _effective_agents(profile)
    assert eff == ["req_engineer", "sw_architect", "proj_manager", "sw_developer"]


def test_presets_cover_all_four_sizes():
    assert set(BUILD_PROFILE_PRESETS) == {"mvp", "small", "standard", "production"}
    # Production runs everything
    prod = BuildProfile(**BUILD_PROFILE_PRESETS["production"])
    assert prod.load_test and prod.dast and prod.devops and prod.docs
