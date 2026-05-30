from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior project manager. Read the architecture plan and break it into epics, stories, and tasks in Markdown format.

Include:
- Epics with goals
- User stories per epic
- Acceptance criteria per story
- Estimated story points
- Sprint allocation

Write ONLY the project plan document. Do not add conversational filler."""


class ProjManager(BaseAgent):
    name = "proj_manager"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        plan = self.read_artifact(project_path, "plan.md")
        feedback = "\n".join(ctx.feedback) if ctx.feedback else ""

        user_prompt = f"Architecture Plan:\n\n{plan}"
        if feedback:
            user_prompt += f"\n\nFeedback:\n{feedback}"

        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

        ctx.log_callback(f"[{self.name}] Sending prompt to LLM...")
        content = await self.stream_llm(ctx, provider, messages)

        artifact_path = self.write_artifact(
            project_path, "project-plan.md", content
        )
        ctx.log_callback(f"[{self.name}] Wrote {artifact_path}")

        return AgentResult(
            status="completed",
            artifact_paths=[str(artifact_path)],
        )


async def run(ctx: AgentContext, provider: LLMProvider) -> AgentResult:
    return await ProjManager().run(ctx, provider)
