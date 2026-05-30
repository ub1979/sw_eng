from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior software developer. Implement all tasks from the project plan.

Read the requirements, architecture plan, and project plan. Write production-ready code.

Output format:
Use file delimiters exactly like:
--- FILE: src/main.py ---
<code>
--- FILE: src/utils.py ---
<code>

Write complete, runnable code. Do not add conversational filler outside file blocks."""


class SwDeveloper(BaseAgent):
    name = "sw_developer"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        requirements = self.read_artifact(project_path, "requirements.md")
        plan = self.read_artifact(project_path, "plan.md")
        project_plan = self.read_artifact(project_path, "project-plan.md")
        feedback = "\n".join(ctx.feedback) if ctx.feedback else ""

        user_prompt = (
            f"Requirements:\n\n{requirements}\n\n"
            f"Architecture Plan:\n\n{plan}\n\n"
            f"Project Plan:\n\n{project_plan}"
        )
        if feedback:
            user_prompt += f"\n\nFeedback:\n{feedback}"

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
    return await SwDeveloper().run(ctx, provider)
