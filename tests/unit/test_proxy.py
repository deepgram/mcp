"""Tests for deepgram_mcp.proxy."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from deepgram_mcp.proxy import DEFAULT_BASE_URL, _run_sse_server, run_proxy


class TestDefaultBaseUrl:
    def test_value(self) -> None:
        assert DEFAULT_BASE_URL == "https://api.dx.deepgram.com"

    def test_no_trailing_slash(self) -> None:
        assert not DEFAULT_BASE_URL.endswith("/")


class TestRunProxy:
    async def test_constructs_correct_mcp_url(self, mcp_stack: dict[str, Any]) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url="https://api.dx.deepgram.com",
            debug=False,
        )
        mcp_stack["streamablehttp_client"].assert_called_once_with(
            url="https://api.dx.deepgram.com/kapa/mcp",
            headers={"Authorization": "Token test-key"},
        )

    async def test_strips_trailing_slash_from_base_url(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url="https://api.dx.deepgram.com/",
            debug=False,
        )
        mcp_stack["streamablehttp_client"].assert_called_once_with(
            url="https://api.dx.deepgram.com/kapa/mcp",
            headers={"Authorization": "Token test-key"},
        )

    async def test_authorization_header_uses_token_scheme(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="my-secret-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        _, call_kwargs = mcp_stack["streamablehttp_client"].call_args
        assert call_kwargs["headers"] == {"Authorization": "Token my-secret-key"}

    async def test_initializes_remote_session(self, mcp_stack: dict[str, Any]) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        mcp_stack["remote"].initialize.assert_awaited_once()

    async def test_discovers_remote_tools(self, mcp_stack: dict[str, Any]) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        mcp_stack["remote"].list_tools.assert_awaited_once()

    async def test_debug_prints_connection_url(
        self, mcp_stack: dict[str, Any], capsys: pytest.CaptureFixture[str]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=True,
        )
        stderr = capsys.readouterr().err
        assert "[DEBUG] Connecting to" in stderr
        assert "kapa/mcp" in stderr

    async def test_debug_prints_tool_names(
        self, mcp_stack: dict[str, Any], capsys: pytest.CaptureFixture[str]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=True,
        )
        stderr = capsys.readouterr().err
        assert "[DEBUG] Remote tools:" in stderr
        assert "ask_deepgram" in stderr

    async def test_no_debug_output_when_disabled(
        self, mcp_stack: dict[str, Any], capsys: pytest.CaptureFixture[str]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        assert capsys.readouterr().err == ""

    async def test_stdio_transport_uses_stdio_server(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        mcp_stack["stdio_server"].assert_called_once()

    async def test_stdio_transport_runs_local_server(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        mcp_stack["local"].run.assert_awaited_once()

    async def test_sse_transport_does_not_use_stdio_server(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        mock_sse_server = AsyncMock()
        with patch("deepgram_mcp.proxy._run_sse_server", mock_sse_server):
            await run_proxy(
                transport="sse",
                host="127.0.0.1",
                port=8000,
                api_key="test-key",
                base_url=DEFAULT_BASE_URL,
                debug=False,
            )
        mcp_stack["stdio_server"].assert_not_called()

    async def test_sse_transport_calls_run_sse_server(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        mock_sse_server = AsyncMock()
        with patch("deepgram_mcp.proxy._run_sse_server", mock_sse_server):
            await run_proxy(
                transport="sse",
                host="10.0.0.1",
                port=9090,
                api_key="test-key",
                base_url=DEFAULT_BASE_URL,
                debug=False,
            )
        mock_sse_server.assert_awaited_once()
        _, _, host, port = mock_sse_server.call_args.args
        assert host == "10.0.0.1"
        assert port == 9090

    async def test_unknown_transport_does_nothing(
        self, mcp_stack: dict[str, Any]
    ) -> None:
        """Unknown transports silently no-op — validation is the caller's job."""
        await run_proxy(
            transport="websocket",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url=DEFAULT_BASE_URL,
            debug=False,
        )
        mcp_stack["stdio_server"].assert_not_called()
        mcp_stack["local"].run.assert_not_awaited()

    async def test_custom_base_url(self, mcp_stack: dict[str, Any]) -> None:
        await run_proxy(
            transport="stdio",
            host="127.0.0.1",
            port=8000,
            api_key="test-key",
            base_url="https://staging.api.deepgram.com",
            debug=False,
        )
        mcp_stack["streamablehttp_client"].assert_called_once_with(
            url="https://staging.api.deepgram.com/kapa/mcp",
            headers={"Authorization": "Token test-key"},
        )


class TestRunSseServer:
    async def test_binds_to_correct_host_and_port(self) -> None:
        mock_uvicorn_server = AsyncMock()
        mock_config_cls = MagicMock()

        with (
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch("uvicorn.Config", mock_config_cls),
            patch("mcp.server.sse.SseServerTransport"),
            patch("starlette.applications.Starlette"),
            patch("starlette.routing.Route"),
        ):
            await _run_sse_server(
                server=MagicMock(),
                init_options=MagicMock(),
                host="0.0.0.0",
                port=3000,
            )

        _, config_kwargs = mock_config_cls.call_args
        assert config_kwargs["host"] == "0.0.0.0"
        assert config_kwargs["port"] == 3000

    async def test_calls_uvicorn_serve(self) -> None:
        mock_uvicorn_server = AsyncMock()

        with (
            patch("uvicorn.Server", return_value=mock_uvicorn_server),
            patch("uvicorn.Config"),
            patch("mcp.server.sse.SseServerTransport"),
            patch("starlette.applications.Starlette"),
            patch("starlette.routing.Route"),
        ):
            await _run_sse_server(
                server=MagicMock(),
                init_options=MagicMock(),
                host="127.0.0.1",
                port=8000,
            )

        mock_uvicorn_server.serve.assert_awaited_once()

    async def test_log_level_is_warning(self) -> None:
        mock_config_cls = MagicMock()
        mock_server_instance = AsyncMock()
        mock_server_cls = MagicMock(return_value=mock_server_instance)

        with (
            patch("uvicorn.Server", mock_server_cls),
            patch("uvicorn.Config", mock_config_cls),
            patch("mcp.server.sse.SseServerTransport"),
            patch("starlette.applications.Starlette"),
            patch("starlette.routing.Route"),
        ):
            await _run_sse_server(
                server=MagicMock(),
                init_options=MagicMock(),
                host="127.0.0.1",
                port=8000,
            )

        _, config_kwargs = mock_config_cls.call_args
        assert config_kwargs["log_level"] == "warning"

    async def test_creates_sse_transport_with_messages_path(self) -> None:
        mock_sse_cls = MagicMock()
        mock_server_instance = AsyncMock()
        mock_server_cls = MagicMock(return_value=mock_server_instance)

        with (
            patch("uvicorn.Server", mock_server_cls),
            patch("uvicorn.Config"),
            patch("mcp.server.sse.SseServerTransport", mock_sse_cls),
            patch("starlette.applications.Starlette"),
            patch("starlette.routing.Route"),
        ):
            await _run_sse_server(
                server=MagicMock(),
                init_options=MagicMock(),
                host="127.0.0.1",
                port=8000,
            )

        mock_sse_cls.assert_called_once_with("/messages")
