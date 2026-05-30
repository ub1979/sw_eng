from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior code reviewer. Review the code against the architecture plan and project plan.

Provide:
- Summary of code quality
- Issues found (if any)
- Recommendations

If issues are found that require developer fixes, start the report with:
NEEDS_FIX: true

Otherwise start with:
NEEDS_FIX: false

Write ONLY the review report. Do not add conversational filler."""


class CodeReviewer(BaseAgent):
    name = "code_reviewer"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        codebase = self.read_all_artifacts(
            project_path, extensions=[".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml", ".md"]
        )
        plan = self.read_artifact(project_path, "plan.md")
        project_plan = self.read_artifact(project_path, "project-plan.md")

        files_summary = "\n\n".join(
            f"--- {path} ---\n{content[:2000]}"
            for path, content in codebase.items()
        )

        user_prompt = (
            f"Architecture Plan:\n\n{plan}\n\n"
            f"Project Plan:\n\n{project_plan}\n\n"
            f"Codebase:\n\n{files_summary}"
        )

        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

        ctx.log_callback(f"[{self.name}] Sending prompt to LLM...")
        content = await self.stream_llm(ctx, provider, messages)

        artifact_path = self.write_artifact(
            project_path, "review-report.md", content
        )
        ctx.log_callback(f"[{self.name}] Wrote {artifact_path}")

        needs_fix = "NEEDS_FIX: true" in content.splitlines()[:5]

        return AgentResult(
            status="completed",
            artifact_paths=[str(artifact_path)],
            needs_fix=needs_fix,
        )


async def run(ctx: AgentContext, provider: LLMProvider) -> AgentResult:
    return await CodeReviewer().run(ctx, provider)
