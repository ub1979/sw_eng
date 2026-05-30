from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior DevOps engineer. Set up CI/CD, Docker, monitoring, and backups.

Read the codebase and architecture plan. Produce:

--- FILE: DEPLOYMENT.md ---
<deployment guide>
--- FILE: Dockerfile ---
<Dockerfile>
--- FILE: docker-compose.yml ---
<compose file>
--- FILE: .github/workflows/ci.yml ---
<CI workflow>

Write production-ready configs. Do not add conversational filler outside file blocks."""


class DevOpsEngineer(BaseAgent):
    name = "devops_engineer"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        plan = self.read_artifact(project_path, "plan.md")
        codebase = self.read_all_artifacts(
            project_path, extensions=[".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml"]
        )

        files_summary = "\n\n".join(
            f"--- {path} ---\n{content[:1000]}"
            for path, content in codebase.items()
        )

        user_prompt = (
            f"Architecture Plan:\n\n{plan}\n\n"
            f"Codebase:\n\n{files_summary}"
        )

        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

        ctx.log_callback(f"[{self.name}] Sending prompt to LLM...")
        content = await self.stream_llm(ctx, provider, messages)

        files = self.parse_multiple_files(content)
        artifact_paths = self.write_multiple_artifacts(project_path, files)

        for path in artifact_paths:
            ctx.log_callback(f"[{self.name}] Wrote {path}")

        return AgentResult(
            status="completed",
            artifact_paths=artifact_paths,
        )


async def run(ctx: AgentContext, provider: LLMProvider) -> AgentResult:
    return await DevOpsEngineer().run(ctx, provider)
