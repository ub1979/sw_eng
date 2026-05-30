import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.providers import ClaudeProvider, GeminiProvider, OllamaProvider, create_provider


@pytest.mark.asyncio
async def test_ollama_provider_health_check_success():
    provider = OllamaProvider(base_url="http://localhost:11434")
    mock_model = Mock()
    mock_model.model = "llama3.2"
    with patch.object(provider._client, "list", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = Mock(models=[mock_model])
        result = await provider.health_check()
        assert result["available"] is True
        assert "llama3.2" in result["models"]


@pytest.mark.asyncio
async def test_ollama_provider_health_check_failure():
    provider = OllamaProvider(base_url="http://localhost:11434")
    with patch.object(provider._client, "list", new_callable=AsyncMock) as mock_list:
        mock_list.side_effect = Exception("Connection refused")
        result = await provider.health_check()
        assert result["available"] is False
        assert "How to fix" in result["error"] or "Start it with" in result["error"]


@pytest.mark.asyncio
async def test_claude_provider_health_check_missing_binary():
    provider = ClaudeProvider(cli_path="/nonexistent/claude")
    with patch("app.providers.shutil.which", return_value=None):
        result = await provider.health_check()
        assert result["available"] is False
        assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_gemini_provider_health_check_missing_binary():
    provider = GeminiProvider(cli_path="/nonexistent/gemini")
    with patch("app.providers.shutil.which", return_value=None):
        result = await provider.health_check()
        assert result["available"] is False
        assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_claude_provider_chat_success():
    provider = ClaudeProvider(cli_path="claude")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b'{"content": "hello"}', b""))

    with patch("app.providers.shutil.which", return_value="/usr/bin/claude"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.chat([{"role": "user", "content": "hi"}]):
                chunks.append(chunk)
            assert len(chunks) == 1
            assert "hello" in chunks[0].content
            assert chunks[0].done is True


@pytest.mark.asyncio
async def test_claude_provider_chat_error():
    provider = ClaudeProvider(cli_path="claude")
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate = AsyncMock(return_value=(b"", b"claude error"))

    with patch("app.providers.shutil.which", return_value="/usr/bin/claude"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.chat([{"role": "user", "content": "hi"}]):
                chunks.append(chunk)
            assert len(chunks) == 1
            assert chunks[0].error is not None
            assert "claude error" in chunks[0].error


@pytest.mark.asyncio
async def test_gemini_provider_health_check_uses_version_first():
    provider = GeminiProvider(cli_path="gemini")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"gemini 1.0.0", b""))

    with patch("app.providers.shutil.which", return_value="/usr/bin/gemini"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await provider.health_check()
            assert result["available"] is True
            call_args = mock_exec.call_args
            assert "--version" in call_args[0]


@pytest.mark.asyncio
async def test_gemini_provider_chat_uses_skip_trust():
    provider = GeminiProvider(cli_path="gemini")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"hello from gemini", b""))

    with patch("app.providers.shutil.which", return_value="/usr/bin/gemini"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            chunks = []
            async for chunk in provider.chat([{"role": "user", "content": "hi"}]):
                chunks.append(chunk)
            call_args = mock_exec.call_args
            assert "--skip-trust" in call_args[0]
            assert chunks[0].content == "hello from gemini"


@pytest.mark.asyncio
async def test_gemini_auto_detect_agy():
    with patch("app.providers.shutil.which", side_effect=lambda x: x == "agy"):
        provider = GeminiProvider()
        assert provider.cli_path == "agy"


@pytest.mark.asyncio
async def test_gemini_auto_detect_gemini_fallback():
    with patch("app.providers.shutil.which", side_effect=lambda x: x == "gemini"):
        provider = GeminiProvider()
        assert provider.cli_path == "gemini"


@pytest.mark.asyncio
async def test_create_provider_factory():
    p = create_provider("ollama", "llama3.2")
    assert p.name == "ollama"
    assert p.model == "llama3.2"

    p = create_provider("claude")
    assert p.name == "claude"

    p = create_provider("gemini")
    assert p.name == "gemini"

    with pytest.raises(ValueError, match="Unknown provider"):
        create_provider("unknown")


@pytest.mark.asyncio
async def test_claude_list_models_returns_curated_list():
    from app.config import CLAUDE_MODELS
    provider = ClaudeProvider(cli_path="claude")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"1.0.0", b""))
    with patch("app.providers.shutil.which", return_value="/usr/bin/claude"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            models = await provider.list_models()
            assert models == CLAUDE_MODELS
            assert len(models) > 1


@pytest.mark.asyncio
async def test_gemini_list_models_returns_curated_list():
    from app.config import GEMINI_MODELS
    provider = GeminiProvider(cli_path="gemini")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"1.0.0", b""))
    with patch("app.providers.shutil.which", return_value="/usr/bin/gemini"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            models = await provider.list_models()
            assert models == GEMINI_MODELS
            assert len(models) > 1


@pytest.mark.asyncio
async def test_claude_chat_passes_selected_model():
    provider = ClaudeProvider(cli_path="claude", model="haiku")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b'{"content": "ok"}', b""))
    with patch("app.providers.shutil.which", return_value="/usr/bin/claude"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            async for _ in provider.chat([{"role": "user", "content": "hi"}]):
                pass
            argv = mock_exec.call_args[0]
            assert "--model" in argv
            assert argv[argv.index("--model") + 1] == "haiku"


@pytest.mark.asyncio
async def test_gemini_chat_passes_selected_model():
    provider = GeminiProvider(cli_path="gemini", model="gemini-2.5-pro")
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"ok", b""))
    with patch("app.providers.shutil.which", return_value="/usr/bin/gemini"):
        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            async for _ in provider.chat([{"role": "user", "content": "hi"}]):
                pass
            argv = mock_exec.call_args[0]
            assert "-m" in argv
            assert argv[argv.index("-m") + 1] == "gemini-2.5-pro"


@pytest.mark.asyncio
async def test_ollama_provider_chat_streaming():
    provider = OllamaProvider(base_url="http://localhost:11434", model="llama3.2")
    mock_chunk = Mock()
    mock_chunk.message.content = "hello"
    mock_chunk.done = False
    mock_chunk2 = Mock()
    mock_chunk2.message.content = " world"
    mock_chunk2.done = True

    async def async_gen():
        yield mock_chunk
        yield mock_chunk2

    with patch.object(provider._client, "chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = async_gen()
        chunks = []
        async for c in provider.chat([{"role": "user", "content": "hi"}]):
            chunks.append(c)
        assert len(chunks) == 2
        assert chunks[0].content == "hello"
        assert chunks[1].content == " world"
