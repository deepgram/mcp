"""Tests for deepgram_mcp.__main__."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestSignalHandler:
    def test_calls_os_exit(self, capsys: pytest.CaptureFixture[str]) -> None:
        from deepgram_mcp.__main__ import signal_handler

        with patch("os._exit") as mock_exit:
            signal_handler(2, None)
        mock_exit.assert_called_once_with(0)

    def test_prints_message_to_stderr(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from deepgram_mcp.__main__ import signal_handler

        with patch("os._exit"):
            signal_handler(2, None)
        assert "stopped by user" in capsys.readouterr().err


class TestMain:
    def _run_main(self, argv: list[str]) -> None:
        from deepgram_mcp.__main__ import main

        with patch("sys.argv", ["deepgram-mcp", *argv]):
            main()

    def test_missing_api_key_exits_1(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("sys.argv", ["deepgram-mcp"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            from deepgram_mcp.__main__ import main

            main()
        assert exc_info.value.code == 1

    def test_missing_api_key_prints_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("sys.argv", ["deepgram-mcp"]),
            pytest.raises(SystemExit),
        ):
            from deepgram_mcp.__main__ import main

            main()
        assert "API key" in capsys.readouterr().err

    def test_api_key_from_env(self) -> None:
        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "env-key"}),
            patch("sys.argv", ["deepgram-mcp"]),
            patch("asyncio.run") as mock_asyncio_run,
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()
        mock_asyncio_run.assert_called_once()

    def test_api_key_from_flag(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("sys.argv", ["deepgram-mcp", "--api-key", "flag-key"]),
            patch("asyncio.run") as mock_asyncio_run,
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()
        mock_asyncio_run.assert_called_once()

    def test_default_transport_is_stdio(self) -> None:
        captured_kwargs: dict = {}

        def capture_run(coro: object) -> None:
            import inspect

            if inspect.iscoroutine(coro):
                # Extract the kwargs from the coroutine's cr_frame locals
                frame = coro.cr_frame
                if frame:
                    captured_kwargs.update(frame.f_locals)
                coro.close()

        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch("sys.argv", ["deepgram-mcp"]),
            patch("asyncio.run", side_effect=capture_run),
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()

        assert captured_kwargs.get("transport") == "stdio"

    def test_transport_sse_passed_through(self) -> None:
        captured_kwargs: dict = {}

        def capture_run(coro: object) -> None:
            import inspect

            if inspect.iscoroutine(coro):
                frame = coro.cr_frame
                if frame:
                    captured_kwargs.update(frame.f_locals)
                coro.close()

        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch("sys.argv", ["deepgram-mcp", "--transport", "sse"]),
            patch("asyncio.run", side_effect=capture_run),
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()

        assert captured_kwargs.get("transport") == "sse"

    def test_debug_flag_passed_through(self) -> None:
        captured_kwargs: dict = {}

        def capture_run(coro: object) -> None:
            import inspect

            if inspect.iscoroutine(coro):
                frame = coro.cr_frame
                if frame:
                    captured_kwargs.update(frame.f_locals)
                coro.close()

        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch("sys.argv", ["deepgram-mcp", "--debug"]),
            patch("asyncio.run", side_effect=capture_run),
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()

        assert captured_kwargs.get("debug") is True

    def test_keyboard_interrupt_exits_0(self) -> None:
        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch("sys.argv", ["deepgram-mcp"]),
            patch("asyncio.run", side_effect=KeyboardInterrupt),
            patch("signal.signal"),
            pytest.raises(SystemExit) as exc_info,
        ):
            from deepgram_mcp.__main__ import main

            main()
        assert exc_info.value.code == 0

    def test_exception_exits_1(self) -> None:
        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch("sys.argv", ["deepgram-mcp"]),
            patch("asyncio.run", side_effect=ConnectionRefusedError("refused")),
            patch("signal.signal"),
            pytest.raises(SystemExit) as exc_info,
        ):
            from deepgram_mcp.__main__ import main

            main()
        assert exc_info.value.code == 1

    def test_exception_prints_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch("sys.argv", ["deepgram-mcp"]),
            patch(
                "asyncio.run", side_effect=ConnectionRefusedError("refused")
            ),
            patch("signal.signal"),
            pytest.raises(SystemExit),
        ):
            from deepgram_mcp.__main__ import main

            main()
        assert "refused" in capsys.readouterr().err

    def test_custom_port_and_host(self) -> None:
        captured_kwargs: dict = {}

        def capture_run(coro: object) -> None:
            import inspect

            if inspect.iscoroutine(coro):
                frame = coro.cr_frame
                if frame:
                    captured_kwargs.update(frame.f_locals)
                coro.close()

        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch(
                "sys.argv",
                ["deepgram-mcp", "--transport", "sse", "--port", "9090", "--host", "0.0.0.0"],
            ),
            patch("asyncio.run", side_effect=capture_run),
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()

        assert captured_kwargs.get("port") == 9090
        assert captured_kwargs.get("host") == "0.0.0.0"

    def test_custom_base_url(self) -> None:
        captured_kwargs: dict = {}

        def capture_run(coro: object) -> None:
            import inspect

            if inspect.iscoroutine(coro):
                frame = coro.cr_frame
                if frame:
                    captured_kwargs.update(frame.f_locals)
                coro.close()

        with (
            patch.dict(os.environ, {"DEEPGRAM_API_KEY": "test-key"}),
            patch(
                "sys.argv",
                ["deepgram-mcp", "--base-url", "https://staging.api.deepgram.com"],
            ),
            patch("asyncio.run", side_effect=capture_run),
            patch("signal.signal"),
        ):
            from deepgram_mcp.__main__ import main

            main()

        assert captured_kwargs.get("base_url") == "https://staging.api.deepgram.com"
