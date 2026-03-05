```markdown
<div align="center">

# 🎙️ stepcast

**The lightweight observability layer for Python scripts and pipelines.**
**Stream logs, monitor progress, and visualize execution in real-time.**
```

> **Every Python script deserves a voice.**

`stepcast` wraps any Python function in a named, observable step. When a pipeline runs, each step announces itself — label, live output, duration, pass/fail — in the terminal, Colab notebook, or your local web dashboard. 

**Zero required dependencies. Works on every OS. Readable by everyone.**

<br/>

[![PyPI version](https://img.shields.io/pypi/v/stepcast.svg?style=for-the-badge&color=blue)](https://pypi.org/project/stepcast/)
[![Python](https://img.shields.io/pypi/pyversions/stepcast.svg?style=for-the-badge&logo=python&logoColor=white)](https://pypi.org/project/stepcast/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/bosekarmegam/stepcast.svg?style=for-the-badge&logo=github&color=yellow)](https://github.com/bosekarmegam/stepcast/stargazers)

</div>

<br/>

## 📖 Table of Contents
- [Preview & Presentation](#-preview--presentation)
- [Features](#-features)
- [Installation](#-installation)
- [Quickstart Guide](#-quickstart-guide)
- [Web Dashboard](#-web-dashboard)
- [AI Narration](#-gemini-ai-narration)
- [Documentation & Community](#-documentation--community)

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 📡 **Live output streaming** | Every `print()` inside a step streams to terminal in real time |
| ✅ **Pass / ❌ Fail / ⏭ Skip** | Clear visual status with timing for every step |
| 🔄 **Retry with backoff** | `retries=3, retry_delay=2.0` with exponential backoff |
| ⏱️ **Timeout enforcement** | Per-step timeout raises `StepFailedError` cleanly |
| 💨 **Dry run mode** | Preview all steps without executing anything |
| 🤖 **Gemini AI narration** | Optional: explains what each step did in plain English |
| 🌐 **Local web dashboard** | `stepcast serve` → run history at `localhost:4321` |
| 🐳 **Docker self-hosted** | One command team dashboard (`docker-compose up`) |
| 📓 **Google Colab** | Native auth + save to Drive |
| 🎨 **Rich support** | Beautiful spinners + colour when `rich` is installed |
| 🌍 **i18n ready** | All strings in locale files, community-translated |
| 🔒 **Zero dep core** | Pure stdlib — `pip install stepcast` just works |

---

## � Installation

```bash
# Core library (zero dependencies)
pip install stepcast

# Add beautiful terminal formatting
pip install "stepcast[rich]"

# Add the local web dashboard
pip install "stepcast[dashboard]"

# Add AI narration using Google Gemini
pip install "stepcast[gemini]"

# Install everything!
pip install "stepcast[all]"
```

---

## 🚀 Quickstart Guide

Building an observable pipeline takes seconds:

```python
from stepcast import Pipeline

pipe = Pipeline("My First Pipeline")

@pipe.step("Download data", retries=2)
def download():
    print("Fetching records...")
    return [1, 2, 3]

@pipe.step("Process data")
def process(data: list):
    result = sum(data)
    print(f"Sum = {result}")
    return result

@pipe.step("Save results", skip_if=lambda: False)
def save(total: int):
    print(f"Saving total: {total}")

report = pipe.run()
print(report.summary())
```

**What you see in the terminal:**
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📡  My First Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ▶  Download data...
     → Fetching records...
  ✅  Done  (0.01s)

  ▶  Process data...
     → Sum = 6
  ✅  Done  (0.00s)

  ▶  Save results...
     → Saving total: 6
  ✅  Done  (0.00s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  3 of 3 steps passed   Total: 0.01s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🌐 Web Dashboard

Monitor your runs graphically with the built-in local dashboard!

```bash
stepcast serve
# → Opens http://localhost:4321 automatically
# → Shows your run history, step details, analytics
```

**Stream a live run:**
```python
pipe = Pipeline("ETL Job", dashboard=True)
pipe.run()  # Watch it run live in your browser!
```

---

## 🤖 Gemini AI Narration

`stepcast` can use **Google Gemini 2.5 Flash** to automatically summarize what your code did in plain English. Ideal for long builds or sharing logs with non-technical team members!

```bash
# Get your free key from Google AI Studio
export STEPCAST_GEMINI_API_KEY="AIza..."
```

```python
pipe = Pipeline("Data Cruncher", narrate=True)
# Terminal Output:
#   ▶  Clean Dataset...
#      💬 "The pipeline removed 45 invalid rows and imputed missing values in 1.2s."
#   ✅  Done
```

---

## 🩺 Powerful CLI tools

```bash
stepcast version         # Print installed version
stepcast doctor          # Diagnose your environment (Python, OS, packages, keys)
stepcast config set gemini_api_key YOUR_KEY
stepcast run script.py   # Run a pipeline and ensure proper exit codes
```

---

## � Documentation & Community

Dive deeper into how `stepcast` works:

- 📖 **[Quickstart & Core Concepts](docs/quickstart.md)**
- 📘 **[Full API Reference](docs/api_reference.md)**
- 📊 **[Dashboard Guide](docs/dashboard.md)**
- 🤖 **[AI Narration Setup](docs/gemini_narration.md)**
- 📓 **[Colab Integration](docs/colab_guide.md)**
- 🛡️ **[Security Policy](SECURITY.md)**
- 📝 **[Changelog](CHANGELOG.md)**

### Joining the Project

Contributions are highly welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions, PR processes, and testing standards. We especially welcome translations for the locale files!

- � [Report a Bug](https://github.com/bosekarmegam/stepcast/issues)

---

## 📜 License & Attribution

<div align="center">

Released under the [MIT License](LICENSE) © 2026.

Built with passion for the global Python community by **[Suneel Bose K](https://github.com/bosekarmegam)**.

</div>
