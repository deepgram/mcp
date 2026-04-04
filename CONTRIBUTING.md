# Contributing

Contributions are welcome! Bug fixes, features, and documentation improvements are all appreciated.

## Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/mcp.git
cd mcp

# Install dependencies
uv sync --extra dev

# Run checks
uv run ruff format src/
uv run ruff check src/
uv run mypy src/
uv run pytest
```

## Development Workflow

1. **Create a branch** from `main`
2. **Make your changes**
3. **Run checks** to ensure everything passes
4. **Submit a pull request**

## Conventions

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add streamable-http transport
fix: handle connection timeout gracefully
docs: add Zed editor setup instructions
test: add SSE transport tests
chore: update dependencies
```

### Code Style

- **Formatter/linter:** `ruff` (line-length 88, target py310)
- **Type checker:** `mypy` (strict mode)
- **Imports:** Use `from __future__ import annotations` for forward references

### Testing

```bash
uv run pytest
uv run pytest -v --cov
```

## Reporting Issues

- **Bugs:** Use the [bug report template](https://github.com/deepgram/mcp/issues/new?template=bug_report.yml)
- **Features:** Use the [feature request template](https://github.com/deepgram/mcp/issues/new?template=feature_request.yml)
- **Security:** See [SECURITY.md](.github/SECURITY.md)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
