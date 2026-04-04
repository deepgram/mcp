# deepgram-mcp

Deepgram's [Model Context Protocol](https://modelcontextprotocol.io) server — gives AI editors (Claude Code, Cursor, Windsurf, and others) direct access to Deepgram's speech, transcription, and audio intelligence tools.

## Why deepgram-mcp is different

Most MCP servers ship tools as hardcoded Python. When the provider adds a new tool, you must upgrade the package to get it.

`deepgram-mcp` fetches its tool list from Deepgram's API at runtime. New tools appear in your editor the next time you connect — no package upgrade required.

## Requirements

A **Deepgram API key**. Get one free at [console.deepgram.com](https://console.deepgram.com).

Set it as an environment variable:

```bash
export DEEPGRAM_API_KEY=your_api_key_here
```

## Installation

```bash
pip install deepgram-mcp
```

## Editor setup

### Claude Code

Add to `.mcp.json` in your project root (or `~/.claude/mcp.json` for global):

```json
{
  "mcpServers": {
    "deepgram": {
      "command": "deepgram-mcp",
      "env": {
        "DEEPGRAM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Or via CLI:

```bash
claude mcp add deepgram -- deepgram-mcp
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "deepgram": {
      "command": "deepgram-mcp",
      "env": {
        "DEEPGRAM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Windsurf

Add to your Windsurf MCP config:

```json
{
  "mcpServers": {
    "deepgram": {
      "command": "deepgram-mcp",
      "env": {
        "DEEPGRAM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Usage

### stdio (default — for editor integration)

```bash
deepgram-mcp --api-key your_api_key_here
```

### SSE (HTTP server)

```bash
deepgram-mcp --transport sse --port 8000
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--transport` | `stdio` | Transport mode: `stdio` or `sse` |
| `--port` | `8000` | Port for SSE server |
| `--host` | `127.0.0.1` | Host for SSE server |
| `--api-key` | `$DEEPGRAM_API_KEY` | Deepgram API key |
| `--base-url` | `https://api.dx.deepgram.com` | Deepgram developer API base URL |
| `--debug` | `false` | Print debug info to stderr |

## Use as a library

```python
import asyncio
from deepgram_mcp import run_proxy

asyncio.run(run_proxy(
    transport="stdio",
    host="127.0.0.1",
    port=8000,
    api_key="your_api_key_here",
    base_url="https://api.dx.deepgram.com",
    debug=False,
))
```

## Deepgram CLI

If you use the [Deepgram CLI](https://github.com/deepgram/cli), `dg mcp` wraps this package and handles authentication automatically:

```bash
dg mcp
dg mcp --transport sse --port 8000
```

## License

MIT — see [LICENSE](./LICENSE).
