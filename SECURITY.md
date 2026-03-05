# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please report vulnerabilities privately:

1. Email the maintainer directly via GitHub: [@bosekarmegam](https://github.com/bosekarmegam)
2. Include a clear description of the vulnerability, steps to reproduce, and potential impact
3. We will acknowledge receipt within 48 hours
4. We aim to resolve critical issues within 7 days

## Disclosure Process

- **90-day embargo** from the date of private disclosure
- We will coordinate a public disclosure date with the reporter
- A CVE will be requested for confirmed vulnerabilities with significant impact
- Security advisories will be published via GitHub Security Advisories

## Security Principles in stepcast

- **Zero secrets logging** — stdout capture always runs through `scrub_stdout()` which redacts API keys, tokens, and passwords
- **No outbound network calls in core** — the core library never connects to the internet
- **User-owned API keys** — `stepcast` never holds, proxies, or transmits your Gemini API key
- **Config file permissions** — `~/.stepcast/config.toml` is created with `chmod 600` on Linux/macOS
- **Path traversal protection** — all user-provided file paths are sanitised before use

## Known Risk Areas

- The `dashboard` optional dependency runs a local web server. By default it binds to `127.0.0.1` (localhost only). **Never expose the dashboard with `STEPCAST_HOST=0.0.0.0` without setting `STEPCAST_AUTH_KEY`**.
- The Gemini integration sends step stdout to Google's API. Do not enable `narrate=True` for steps that may output sensitive data.

Built by [Suneel Bose K](https://github.com/bosekarmegam)
