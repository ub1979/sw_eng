import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.models import AgentContext, AgentResult, StreamChunk
from app.providers import LLMProvider


class BaseAgent(ABC):
    name: str = ""

    @abstractmethod
    def system_prompt(self) -> str:
        raise NotImplementedError

    def build_user_prompt(self, ctx: AgentContext) -> str:
        return ""

    async def stream_llm(
        self,
        ctx: AgentContext,
        provider: LLMProvider,
        messages: list[dict[str, str]],
    ) -> str:
        content_parts: list[str] = []
        async for chunk in provider.chat(messages, stream=True):
            if chunk.error:
                ctx.log_callback(f"[{self.name}] LLM error: {chunk.error}")
                raise RuntimeError(chunk.error)
            content_parts.append(chunk.content)
            if chunk.content:
                ctx.log_callback(chunk.content)
        return "".join(content_parts)

    def write_artifact(
        self, project_path: Path, filename: str, content: str
    ) -> Path:
        path = project_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def read_artifact(self, project_path: Path, filename: str) -> str:
        path = project_path / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def read_all_artifacts(
        self, project_path: Path, extensions: list[str] | None = None
    ) -> dict[str, str]:
        files: dict[str, str] = {}
        if not project_path.exists():
            return files
        for path in project_path.rglob("*"):
            if path.is_file():
                rel = str(path.relative_to(project_path))
                if extensions and not any(
                    rel.endswith(ext) for ext in extensions
                ):
                    continue
                try:
                    files[rel] = path.read_text(encoding="utf-8")
                except Exception as exc:
                    logging.warning(
                        "[%s] Skipping non-text file %s: %s",
                        self.name,
                        rel,
                        exc,
                    )
        return files

    def parse_multiple_files(self, content: str) -> dict[str, str]:
        files: dict[str, str] = {}
        current_path: str | None = None
        current_lines: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("--- FILE:"):
                if current_path is not None:
                    files[current_path] = "\n".join(current_lines).strip(
                        "\n"
                    )
                current_path = stripped[len("--- FILE:"):].strip()
                if current_path.endswith("---"):
                    current_path = current_path[:-3].strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_path is not None:
            files[current_path] = "\n".join(current_lines).strip("\n")

        if not files:
            files["output.md"] = content

        return files

    def write_multiple_artifacts(
        self, project_path: Path, files: dict[str, str]
    ) -> list[str]:
        paths: list[str] = []
        for filename, content in files.items():
            path = self.write_artifact(project_path, filename, content)
            paths.append(str(path))
        return paths

    @abstractmethod
    async def run(
        self, ctx: AgentContext, provider: LLMProvider
    ) -> AgentResult:
        raise NotImplementedError
