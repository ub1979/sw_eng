from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior QA engineer. Test everything — functional, edge cases, security, performance.

Read the codebase, project plan, and requirements. Provide:
- Test strategy summary
- Bugs found (if any) with severity
- Edge cases considered

If bugs are found that require developer fixes, start the report with:
NEEDS_FIX: true

Otherwise start with:
NEEDS_FIX: false

Write ONLY the bug report. Do not add conversational filler."""


def _testing_scope(profile) -> str:
    """Translate the build profile into explicit do/skip instructions for the QA agent.
    Skipping tests here both honors the user's choice and shortens the run."""
    if profile is None:
        return ""
    lines = []
    lines.append("- Full end-to-end UI tests" if getattr(profile, "e2e_tests", True)
                 else "- SKIP full UI end-to-end tests; cover critical paths with a smoke test only")
    lines.append("- Run load/performance testing" if getattr(profile, "load_test", False)
                 else "- SKIP load/performance testing")
    lines.append("- Run dynamic application security testing (DAST)" if getattr(profile, "dast", False)
                 else "- SKIP DAST (dynamic security testing)")
    lines.append("- Run security scanning (SAST + dependency audit)" if getattr(profile, "security_scan", True)
                 else "- SKIP security scanning")
    lines.append("- Verify accessibility (keyboard nav, ARIA, contrast)" if getattr(profile, "accessibility", True)
                 else "- SKIP accessibility checks")
    return "\n".join(lines)


class QaEngineer(BaseAgent):
    name = "qa_engineer"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        codebase = self.read_all_artifacts(
            project_path, extensions=[".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml", ".md"]
        )
        project_plan = self.read_artifact(project_path, "project-plan.md")
        requirements = self.read_artifact(project_path, "requirements.md")

        files_summary = "\n\n".join(
            f"--- {path} ---\n{content[:2000]}"
            for path, content in codebase.items()
        )

        user_prompt = (
            f"Requirements:\n\n{requirements}\n\n"
            f"Project Plan:\n\n{project_plan}\n\n"
            f"Codebase:\n\n{files_summary}"
        )

        scope = _testing_scope(ctx.build_profile)
        if scope:
            user_prompt += f"\n\nTesting scope for this build:\n{scope}"

        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

        ctx.log_callback(f"[{self.name}] Sending prompt to LLM...")
        content = await self.stream_llm(ctx, provider, messages)

        artifact_path = self.write_artifact(
            project_path, "bug-report.md", content
        )
        ctx.log_callback(f"[{self.name}] Wrote {artifact_path}")

        needs_fix = "NEEDS_FIX: true" in content.splitlines()[:5]

        return AgentResult(
            status="completed",
            artifact_paths=[str(artifact_path)],
            needs_fix=needs_fix,
        )


async def run(ctx: AgentContext, provider: LLMProvider) -> AgentResult:
    return await QaEngineer().run(ctx, provider)
