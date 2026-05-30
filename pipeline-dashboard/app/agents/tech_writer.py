from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior technical writer. Generate full documentation suite.

Read all project artifacts. Produce:

--- FILE: README.md ---
<readme>
--- FILE: docs/api.md ---
<api docs>
--- FILE: docs/developer-guide.md ---
<guide>
--- FILE: docs/deployment-guide.md ---
<guide>
--- FILE: docs/user-guide.md ---
<guide>
--- FILE: docs/changelog.md ---
<changelog>

Write professional documentation. Do not add conversational filler outside file blocks."""


class TechWriter(BaseAgent):
    name = "tech_writer"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        artifacts = self.read_all_artifacts(project_path)

        files_summary = "\n\n".join(
            f"--- {path} ---\n{content[:1500]}"
            for path, content in artifacts.items()
        )

        user_prompt = f"Project Artifacts:\n\n{files_summary}"

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
    return await TechWriter().run(ctx, provider)
