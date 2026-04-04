"""Tests for deepgram_mcp.models."""

from __future__ import annotations

import pytest

from deepgram_mcp.models import TransportType


class TestTransportType:
    def test_stdio_value(self) -> None:
        assert TransportType.STDIO == "stdio"

    def test_sse_value(self) -> None:
        assert TransportType.SSE == "sse"

    def test_is_string_enum(self) -> None:
        assert isinstance(TransportType.STDIO, str)
        assert isinstance(TransportType.SSE, str)

    def test_parse_from_string(self) -> None:
        assert TransportType("stdio") is TransportType.STDIO
        assert TransportType("sse") is TransportType.SSE

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            TransportType("websocket")

    def test_only_two_values(self) -> None:
        assert set(TransportType) == {TransportType.STDIO, TransportType.SSE}
