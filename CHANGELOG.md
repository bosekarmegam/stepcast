# Changelog

All notable changes to `stepcast` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] — 2026-03-04

### Fixed
- Fixed linter bugs (`ruff check` passes cleanly)

## [1.0.0] — 2026-03-04

### Added
- `Pipeline` class with full step orchestration
- `@pipe.step()` decorator with `retries`, `retry_delay`, `skip_if`, `timeout`, `tags`, `capture_output`
- `pipe.run(initial, steps, dry_run)` with chained step output
- `RunReport` and `StepResult` dataclasses with JSON serialisation
- `StepFailedError` and `PipelineAbortError` exceptions
- Live stdout streaming (never buffered)
- Unicode terminal output with ASCII fallback for Windows legacy terminals
- Exponential retry backoff
- Per-step timeout enforcement
- `fail_fast` and `dry_run` pipeline modes
- Internationalisation (i18n) system with `en` locale
- Config system: `~/.stepcast/config.toml` + environment variable override
- CLI: `stepcast run`, `doctor`, `version`, `config`, `serve`, `check`
- Local web dashboard (Model A): `stepcast serve` → `localhost:4321`
  - Live WebSocket step streaming
  - Run history with search and filter
  - Per-run detail view
  - Simple analytics
- Docker self-hosted dashboard (Model B): `docker-compose up`
- Optional Gemini AI narration (user's own API key, BYOK)
- Optional Rich library renderer
- Google Colab integration (auth + Drive save)
- `@http_step`, `@db_step`, `@ai_step` optional decorators
- Secret scrubbing from captured stdout
- CI matrix: Python 3.10–3.13 × Linux/macOS/Windows
- 95%+ test coverage on core library

### Notes
- Zero required dependencies — pure Python stdlib in core
- MIT License
- Built by [Suneel Bose K](https://github.com/bosekarmegam)
