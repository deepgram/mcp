"""Core MCP proxy logic — connects to Deepgram's remote MCP server and exposes tools locally."""

from __future__ import annotations

import sys
from typing import Any

DEFAULT_BASE_URL = "https://api.dx.deepgram.com"


async def run_proxy(
    *,
    transport: str,
    host: str,
    port: int,
    api_key: str,
    base_url: str,
    debug: bool,
) -> None:
    """Connect to remote Deepgram MCP server and expose tools locally."""
    import mcp.server.stdio
    import mcp.types as types
    from mcp.client.session import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.server.lowlevel import NotificationOptions, Server
    from mcp.server.models import InitializationOptions

    mcp_url = f"{base_url.rstrip('/')}/kapa/mcp"
    headers = {"Authorization": f"Token {api_key}"}

    if debug:
        print(f"[DEBUG] Connecting to {mcp_url}", file=sys.stderr)

    async with streamablehttp_client(url=mcp_url, headers=headers) as (
        read_stream,
        write_stream,
        _get_session_id,
    ):
        async with ClientSession(read_stream, write_stream) as remote:
            await remote.initialize()

            # Discover remote tools
            tools_result = await remote.list_tools()
            remote_tools: list[types.Tool] = tools_result.tools

            if debug:
                names = [t.name for t in remote_tools]
                print(f"[DEBUG] Remote tools: {names}", file=sys.stderr)

            # Create local server that proxies everything to the remote
            local = Server("Deepgram MCP")

            @local.list_tools()
            async def handle_list_tools() -> list[types.Tool]:
                return remote_tools

            @local.call_tool()
            async def handle_call_tool(
                name: str, arguments: dict[str, Any] | None
            ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
                result = await remote.call_tool(name, arguments or {})
                return result.content  # type: ignore[return-value]

            init_options = InitializationOptions(
                server_name="deepgram-mcp",
                server_version="0.1.10",
                capabilities=local.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )

            if transport == "stdio":
                async with mcp.server.stdio.stdio_server() as (srv_r, srv_w):
                    await local.run(srv_r, srv_w, init_options)
            elif transport == "sse":
                await _run_sse_server(local, init_options, host, port)


async def _run_sse_server(
    server: Any,
    init_options: Any,
    host: str,
    port: int,
) -> None:
    """Run local MCP server with SSE transport."""
    import uvicorn
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route

    sse = SseServerTransport("/messages")

    async def handle_sse(request: Any) -> None:
        async with sse.connect_sse(request.scope, request.receive, request.send) as (
            read,
            write,
        ):
            await server.run(read, write, init_options)

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route(
                "/messages",
                endpoint=sse.handle_post_message,
                methods=["POST"],
            ),
        ]
    )

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    srv = uvicorn.Server(config)
    await srv.serve()
