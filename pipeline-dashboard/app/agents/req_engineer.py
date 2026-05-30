from pathlib import Path

from app.agents.base import BaseAgent
from app.models import AgentContext, AgentResult
from app.providers import LLMProvider


SYSTEM_PROMPT = """You are a Requirements Engineer. Your job is to take a user's project description and produce a comprehensive, well-structured requirements document in Markdown format.

Output format:
- Start with a brief project summary
- List functional requirements (numbered)
- List non-functional requirements (numbered)
- Define success criteria
- Note any assumptions or constraints

Write ONLY the markdown document. Do not add conversational filler."""


class ReqEngineer(BaseAgent):
    name = "req_engineer"

    def system_prompt(self) -> str:
        return SYSTEM_PROMPT

    async def run(self, ctx: AgentContext, provider: LLMProvider) -> AgentResult:
        project_path = Path(ctx.project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        user_description = ""
        if ctx.feedback:
            user_description = "Original description with feedback:\n\n" + "\n".join(ctx.feedback)
        else:
            user_description = "Project description: see pipeline record"

        messages = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_description},
        ]

        artifact_path = project_path / "requirements.md"
        content_parts: list[str] = []

        ctx.log_callback(f"[{self.name}] Sending prompt to LLM...")
        async for chunk in provider.chat(messages, stream=True):
            if chunk.error:
                ctx.log_callback(f"[{self.name}] LLM error: {chunk.error}")
                return AgentResult(status="failed", error_message=chunk.error)
            content_parts.append(chunk.content)
            if chunk.content:
                ctx.log_callback(chunk.content)

        full_content = "".join(content_parts)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        ctx.log_callback(f"[{self.name}] Wrote {artifact_path}")
        return AgentResult(
            status="completed",
            artifact_paths=[str(artifact_path)],
        )


async def run(ctx: AgentContext, provider: LLMProvider) -> AgentResult:
    return await ReqEngineer().run(ctx, provider)
