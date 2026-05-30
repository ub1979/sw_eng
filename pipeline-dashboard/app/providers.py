import asyncio
import json
import shutil
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

import ollama

from app.config import CLAUDE_MODELS, GEMINI_MODELS, settings
from app.models import StreamChunk


FIX_HINTS = {
    "ollama": "Ollama is not running on port 11434. Start it with: ollama serve",
    "claude": "Claude Code CLI not found in PATH. Install it from: https://code.claude.com",
    "gemini": "Gemini or Antigravity CLI not found in PATH. Install agy (Antigravity 2.0) or gemini CLI.",
}


class LLMProvider(ABC):
    name: str = ""

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], stream: bool = True) -> AsyncIterator[StreamChunk]:
        raise NotImplementedError

    @abstractmethod
    async def list_models(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str | None = None, model: str | None = None) -> None:
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or "llama3.2"
        self._client = ollama.AsyncClient(host=self.base_url)

    async def health_check(self) -> dict[str, Any]:
        try:
            resp = await self._client.list()
            models = [m.model for m in resp.models if m.model]
            return {"available": True, "models": models, "error": None}
        except Exception as exc:
            return {
                "available": False,
                "error": f"Ollama unreachable at {self.base_url}: {exc}. {FIX_HINTS['ollama']}",
                "models": [],
            }

    async def list_models(self) -> list[str]:
        result = await self.health_check()
        return result.get("models", [])

    async def chat(self, messages: list[dict[str, str]], stream: bool = True) -> AsyncIterator[StreamChunk]:
        try:
            response = await self._client.chat(
                model=self.model,
                messages=messages,
                stream=stream,
            )
            if stream:
                async for chunk in response:
                    content = chunk.message.content or ""
                    done = chunk.done or False
                    yield StreamChunk(role="assistant", content=content, done=done)
            else:
                content = response.message.content or ""
                yield StreamChunk(role="assistant", content=content, done=True)
        except Exception as exc:
            yield StreamChunk(role="assistant", content="", done=True, error=str(exc))


class ClaudeProvider(LLMProvider):
    name = "claude"

    def __init__(self, cli_path: str | None = None, model: str | None = None) -> None:
        self.cli_path = cli_path or settings.claude_cli_path
        self.models_list = CLAUDE_MODELS
        self.model = model or (CLAUDE_MODELS[0] if CLAUDE_MODELS else "sonnet")

    async def health_check(self) -> dict[str, Any]:
        if not shutil.which(self.cli_path):
            return {
                "available": False,
                "error": f"'{self.cli_path}' not found in PATH. {FIX_HINTS['claude']}",
                "models": [],
            }
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if proc.returncode == 0:
                return {"available": True, "models": self.models_list, "error": None}
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass

        # Fallback: try --help
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_path, "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if proc.returncode == 0:
                return {"available": True, "models": self.models_list, "error": None}
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass

        # Last resort: binary exists but we can't verify it works
        return {
            "available": True,
            "models": self.models_list,
            "error": "Binary found but could not verify. Pipeline may fail if the CLI is misconfigured.",
        }

    async def list_models(self) -> list[str]:
        result = await self.health_check()
        return result.get("models", [])

    async def chat(self, messages: list[dict[str, str]], stream: bool = True) -> AsyncIterator[StreamChunk]:
        prompt = messages[-1].get("content", "")
        system_prompt = ""
        if len(messages) > 1 and messages[0].get("role") == "system":
            system_prompt = messages[0].get("content", "")

        args = [self.cli_path, "-p", prompt, "--bare", "--output-format", "json"]
        if self.model:
            args.extend(["--model", self.model])
        if system_prompt:
            args.extend(["--system-prompt", system_prompt])

        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            if proc.returncode != 0:
                yield StreamChunk(
                    role="assistant",
                    content="",
                    done=True,
                    error=f"Claude CLI error: {stderr.decode().strip() or proc.returncode}",
                )
                return
            try:
                data = json.loads(stdout.decode())
                content = data if isinstance(data, str) else json.dumps(data, indent=2)
            except json.JSONDecodeError:
                content = stdout.decode()
            yield StreamChunk(role="assistant", content=content, done=True)
        except asyncio.TimeoutError:
            yield StreamChunk(role="assistant", content="", done=True, error="Claude CLI timed out after 30 seconds")
        except Exception as exc:
            yield StreamChunk(role="assistant", content="", done=True, error=str(exc))


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, cli_path: str | None = None, model: str | None = None) -> None:
        self.models_list = GEMINI_MODELS
        self.model = model or (GEMINI_MODELS[0] if GEMINI_MODELS else "gemini-2.5-flash")
        if cli_path:
            self.cli_path = cli_path
        elif shutil.which("agy"):
            self.cli_path = "agy"
        elif shutil.which("gemini"):
            self.cli_path = "gemini"
        else:
            self.cli_path = settings.gemini_cli_path

    async def health_check(self) -> dict[str, Any]:
        if not shutil.which(self.cli_path):
            return {
                "available": False,
                "error": f"'{self.cli_path}' not found in PATH. {FIX_HINTS['gemini']}",
                "models": [],
            }
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if proc.returncode == 0:
                return {"available": True, "models": self.models_list, "error": None}
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass

        # Fallback: try --help
        try:
            proc = await asyncio.create_subprocess_exec(
                self.cli_path, "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
            if proc.returncode == 0:
                return {"available": True, "models": self.models_list, "error": None}
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass

        # Last resort: binary exists but we can't verify it works
        return {
            "available": True,
            "models": self.models_list,
            "error": "Binary found but could not verify. Pipeline may fail if the CLI is misconfigured.",
        }

    async def list_models(self) -> list[str]:
        result = await self.health_check()
        return result.get("models", [])

    async def chat(self, messages: list[dict[str, str]], stream: bool = True) -> AsyncIterator[StreamChunk]:
        prompt = messages[-1].get("content", "")
        args = [self.cli_path, "--skip-trust"]
        if self.model:
            args.extend(["-m", self.model])
        args.extend(["-p", prompt])
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
            if proc.returncode != 0:
                yield StreamChunk(
                    role="assistant",
                    content="",
                    done=True,
                    error=f"Gemini CLI error: {stderr.decode().strip() or proc.returncode}",
                )
                return
            content = stdout.decode()
            yield StreamChunk(role="assistant", content=content, done=True)
        except asyncio.TimeoutError:
            yield StreamChunk(role="assistant", content="", done=True, error="Gemini CLI timed out after 30 seconds")
        except Exception as exc:
            yield StreamChunk(role="assistant", content="", done=True, error=str(exc))


def create_provider(name: str, model: str | None = None) -> LLMProvider:
    if name == "ollama":
        return OllamaProvider(model=model)
    if name == "claude":
        return ClaudeProvider(model=model)
    if name == "gemini":
        return GeminiProvider(model=model)
    raise ValueError(f"Unknown provider: {name}")
