from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a senior software architect. Read the provided requirements and produce a complete architecture plan in Markdown format.

Include:
- Tech stack with rationale
- System components and their responsibilities
- Data architecture
- API design (if applicable)
- Security considerations
- Deployment approach

Write ONLY the architecture document. Do not add conversational filler."""


class SwArchitect(BaseAgent):
    name = "sw_architect"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        requirements = self.read_artifact(project_path, "requirements.md")
        feedback = "\n".join(ctx.feedback) if ctx.feedback else ""

        user_prompt = f"Requirements:\n\n{requirements}"
        if feedback:
            user_prompt += f"\n\nFeedback:\n{feedback}"

        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_prompt},
        ]

        ctx.log_callback(f"[{self.name}] Sending prompt to LLM...")
        content = await self.stream_llm(ctx, provider, messages)

        artifact_path = self.write_artifact(project_path, "plan.md", content)
        ctx.log_callback(f"[{self.name}] Wrote {artifact_path}")

        return AgentResult(
            status="completed",
            artifact_paths=[str(artifact_path)],
        )


async def run(ctx: AgentContext, provider: LLMProvider) -> AgentResult:
    return await SwArchitect().run(ctx, provider)
