# Contributing to stepcast

Thank you for helping make `stepcast` better! This guide explains how to contribute.

---

## 🛠️ Development Setup

```bash
git clone https://github.com/bosekarmegam/stepcast
cd stepcast

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.\.venv\Scripts\Activate.ps1    # Windows PowerShell

# Install all dev dependencies
pip install -e ".[dev,dashboard,rich,gemini,colab]"

# Install pre-commit hooks
pre-commit install
```

---

## 🌿 Branch Naming

```
feat/add-http-step-decorator
fix/windows-unicode-fallback
docs/gemini-setup-guide
refactor/extract-ws-manager
test/add-websocket-integration
```

---

## 📝 Commit Messages (Conventional Commits)

```
feat: add @http_step with request/response logging
fix: unicode fallback on Windows cp1252 terminals
docs: add Gemini API key setup guide
test: add WebSocket live stream integration test
refactor: extract ConnectionManager to ws.py
chore: bump ruff to 0.2
```

---

## 🧪 Running Tests

```bash
pytest                              # All tests
pytest -m "not integration"        # Fast tests only (dev mode)
pytest -m smoke                    # Smoke tests only (CI gate)
pytest --cov=stepcast --cov-report=html  # Coverage report
```

---

## ✅ PR Checklist

Before submitting a pull request, verify:

- [ ] All existing tests pass
- [ ] New tests added for new behaviour (coverage maintained)
- [ ] Full type hints on all new/changed functions
- [ ] Docstrings updated (Google style)
- [ ] `CHANGELOG.md` entry added under `[Unreleased]`
- [ ] Zero new **required** dependencies in core
- [ ] Tested on Python 3.10, 3.11, 3.12, 3.13 (or CI covers it)
- [ ] User-facing strings in i18n locale file (not hard-coded)
- [ ] No secrets logged (scrubbing applied where needed)
- [ ] `mypy --strict` passes

---

## 🌍 Adding a Locale Translation

1. Copy `stepcast/locales/en.json`
2. Rename to `stepcast/locales/{locale}.json` (e.g. `es.json`, `zh.json`)
3. Translate all values (keep all keys identical)
4. Submit a PR — no code changes needed!

Target locales: `es` · `zh` · `de` · `fr` · `ja` · `pt` · `hi` · `ar`

---

## 🔒 Security Issues

Please do **not** open a public issue for security vulnerabilities.
See [SECURITY.md](SECURITY.md) for the private disclosure process.

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

Built by [Suneel Bose K](https://github.com/bosekarmegam)
