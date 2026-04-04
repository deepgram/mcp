"""Models for the Deepgram MCP proxy."""

from enum import Enum


class TransportType(str, Enum):
    """Transport types for MCP server."""

    STDIO = "stdio"
    SSE = "sse"
