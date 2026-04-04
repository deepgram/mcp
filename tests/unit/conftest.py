"""Shared fixtures for deepgram-mcp tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_tool() -> MagicMock:
    """A minimal fake MCP tool."""
    tool = MagicMock()
    tool.name = "ask_deepgram"
    return tool


@pytest.fixture
def mock_remote(mock_tool: MagicMock) -> AsyncMock:
    """Mock remote MCP ClientSession."""
    remote = AsyncMock()
    remote.initialize = AsyncMock()
    remote.list_tools = AsyncMock(return_value=MagicMock(tools=[mock_tool]))
    remote.call_tool = AsyncMock(
        return_value=MagicMock(content=[MagicMock(text="result")])
    )
    return remote


@pytest.fixture
def mock_local_server() -> MagicMock:
    """Mock local MCP Server that acts as a passthrough proxy."""
    server = MagicMock()
    server.get_capabilities.return_value = MagicMock()
    server.run = AsyncMock()
    # Decorators: @server.list_tools() and @server.call_tool() each return a
    # callable that accepts the handler function and returns it unchanged.
    server.list_tools.return_value = lambda f: f
    server.call_tool.return_value = lambda f: f
    return server


@pytest.fixture
def mcp_stack(mock_remote: AsyncMock, mock_local_server: MagicMock) -> dict[str, Any]:
    """
    Patch the entire MCP library stack used inside run_proxy().

    Because all MCP imports are deferred (inside the function body), we patch
    the source module attributes rather than names in deepgram_mcp.proxy.
    """
    from unittest.mock import patch

    # streamablehttp_client async context manager → (read, write, get_id)
    streams_cm = AsyncMock()
    streams_cm.__aenter__.return_value = (AsyncMock(), AsyncMock(), MagicMock())
    streams_cm.__aexit__.return_value = None

    # ClientSession async context manager → remote
    session_cm = AsyncMock()
    session_cm.__aenter__.return_value = mock_remote
    session_cm.__aexit__.return_value = None

    # stdio_server async context manager → (read, write)
    stdio_cm = AsyncMock()
    stdio_cm.__aenter__.return_value = (AsyncMock(), AsyncMock())
    stdio_cm.__aexit__.return_value = None

    with (
        patch(
            "mcp.client.streamable_http.streamablehttp_client",
            return_value=streams_cm,
        ) as p_http,
        patch(
            "mcp.client.session.ClientSession",
            return_value=session_cm,
        ) as p_session,
        patch(
            "mcp.server.lowlevel.Server",
            return_value=mock_local_server,
        ) as p_server,
        patch("mcp.server.stdio.stdio_server", return_value=stdio_cm) as p_stdio,
        patch("mcp.server.models.InitializationOptions") as p_init_opts,
        patch("mcp.server.lowlevel.NotificationOptions") as p_notif_opts,
    ):
        yield {
            "streamablehttp_client": p_http,
            "ClientSession": p_session,
            "Server": p_server,
            "stdio_server": p_stdio,
            "InitializationOptions": p_init_opts,
            "NotificationOptions": p_notif_opts,
            "remote": mock_remote,
            "local": mock_local_server,
            "streams_cm": streams_cm,
            "stdio_cm": stdio_cm,
        }
