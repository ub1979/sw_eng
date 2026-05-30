import asyncio
import json
import re
import shlex
from pathlib import Path
from typing import Any

from app.config import settings
from app.dao import SecurityEventDAO
from app.models import SecurityEvent


class GuardrailsBlocked(Exception):
    def __init__(self, message: str, command: str | None = None) -> None:
        super().__init__(message)
        self.command = command


class GuardrailsEngine:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or settings.guardrails_file
        self._config: dict[str, Any] = {}
        self._allowed_executables: set[str] = set()
        self._blocked_patterns: list[str] = []
        self._blocked_arguments: set[str] = set()
        self.load_config(self.config_path)

    def load_config(self, path: Path | None = None) -> None:
        target = path or self.config_path
        if not target.exists():
            self._config = self._default_config()
        else:
            with open(target, "r", encoding="utf-8") as f:
                self._config = json.load(f)
        self._allowed_executables = set(
            self._config.get("allowed_executables", [])
        )
        self._blocked_patterns = self._config.get("blocked_patterns", [])
        self._blocked_arguments = set(
            self._config.get("blocked_arguments", [])
        )

    def validate_command(self, command: str) -> bool:
        max_length = self._config.get("max_command_length", 4096)
        if len(command) > max_length:
            raise GuardrailsBlocked(
                f"Command exceeds max length of {max_length}", command
            )

        for pattern in self._blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                raise GuardrailsBlocked(
                    f"Blocked by pattern: {pattern}", command
                )

        try:
            parts = shlex.split(command)
        except ValueError as exc:
            raise GuardrailsBlocked(
                f"Invalid shell syntax: {exc}", command
            )

        if not parts:
            raise GuardrailsBlocked("Empty command", command)

        executable = parts[0]
        if executable not in self._allowed_executables:
            raise GuardrailsBlocked(
                f"Executable '{executable}' not in allowlist", command
            )

        for arg in parts[1:]:
            if arg in self._blocked_arguments:
                raise GuardrailsBlocked(
                    f"Blocked argument '{arg}'", command
                )

        return True

    def validate_path(self, path: str, project_id: str) -> bool:
        if self._config.get("path_traversal_allowed", False):
            return True

        if ".." in path or path.startswith("/") or path.startswith("~"):
            raise GuardrailsBlocked(
                f"Path traversal blocked: '{path}'", path
            )

        base = (settings.projects_dir / project_id).resolve()
        target = (base / path).resolve()

        try:
            target.relative_to(base)
        except ValueError:
            raise GuardrailsBlocked(
                f"Path '{path}' escapes project sandbox", str(target)
            )

        return True

    async def execute(
        self,
        command: str,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
        pipeline_id: Any = None,
    ) -> asyncio.subprocess.Process:
        self.validate_command(command)

        parts = shlex.split(command)
        try:
            proc = await asyncio.create_subprocess_exec(
                *parts,
                cwd=cwd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            return proc
        except GuardrailsBlocked:
            raise
        except Exception as exc:
            await self._log_security_event(
                event_type="execution_error",
                detail=str(exc),
                command=command,
                pipeline_id=pipeline_id,
            )
            raise

    async def _log_security_event(
        self,
        event_type: str,
        detail: str,
        command: str | None = None,
        pipeline_id: Any = None,
    ) -> None:
        dao = SecurityEventDAO()
        event = SecurityEvent(
            pipeline_id=pipeline_id,
            event_type=event_type,
            detail=detail,
            command=command,
        )
        await dao.create(event)

    def _default_config(self) -> dict[str, Any]:
        return {
            "allowed_executables": [
                "python3",
                "python",
                "node",
                "npm",
                "npx",
                "pip",
                "pip3",
                "pytest",
                "playwright",
                "git",
                "docker",
                "docker-compose",
                "curl",
                "wget",
                "cat",
                "ls",
                "mkdir",
                "cp",
                "mv",
                "rm",
                "touch",
                "echo",
                "find",
                "grep",
                "sed",
                "awk",
                "sort",
                "uniq",
                "wc",
                "tar",
                "zip",
                "unzip",
            ],
            "blocked_patterns": [
                "sudo",
                "rm -rf /",
                "curl.*\\|.*sh",
                "curl.*\\|.*bash",
                "wget.*\\|.*sh",
                ":\\(\\)\\{ :|:\\& \\};:",
                "mkfs",
                "dd if=/dev/zero",
                "> /dev/sda",
                "> /dev/null",
                "chmod 777 /",
                "chown -R",
            ],
            "blocked_arguments": [
                "--no-verify",
                "--insecure",
                "-k",
            ],
            "max_command_length": 4096,
            "path_traversal_allowed": False,
        }
