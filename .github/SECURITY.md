# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in deepgram-mcp, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email [security@deepgram.com](mailto:security@deepgram.com) with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide an estimated timeline for a fix.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |
| < Latest | Best effort |

## Credential Safety

`deepgram-mcp` requires a Deepgram API key passed via `DEEPGRAM_API_KEY` or `--api-key`. The key is sent as an `Authorization` header to `api.dx.deepgram.com` and is never stored or logged.

When using environment variables, ensure they are not exposed in CI output or process listings.
