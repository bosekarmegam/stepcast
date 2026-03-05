# Gemini AI Narration

`stepcast` includes optional AI-powered step narration using **Google Gemini 2.5 Flash**. This feature automatically summarizes the stdout and return values of your pipeline steps into 1-2 plain English sentences. This is ideal for sharing logs with non-technical team members or quickly reviewing long builds.

> **Note:** Narration is designed to be completely resilient. If API calls fail for any reason (e.g., rate limits, network issues), the step will silently complete without narration. AI failures will **never** fail your pipeline.

## Installation

To enable Gemini narration, install the optional `[gemini]` extras:

```bash
pip install "stepcast[gemini]"
```

This installs the required Google GenAI SDKs. `stepcast` natively supports both the modern `google-genai` SDK and the legacy `google-generativeai` package.

## Configuration

`stepcast` uses a "Bring Your Own Key" (BYOK) model. You need a Google Gemini API key to use this feature. You can get a free key from [Google AI Studio](https://aistudio.google.com/).

You can configure your key in two ways:

**Option 1: Environment Variable (Recommended)**

```bash
export STEPCAST_GEMINI_API_KEY="your_api_key_here"
```

**Option 2: CLI Configuration**

```bash
stepcast config set gemini_api_key your_api_key_here
```

## Usage

To enable narration for a pipeline, set the `narrate=True` flag when instantiating the `Pipeline`:

```python
from stepcast import Pipeline

pipe = Pipeline("Data Cruncher", narrate=True)

@pipe.step("Clean Dataset")
def clean():
    print("Removed 45 invalid rows.")
    print("Imputed missing values.")
    return {"cleaned": True, "rows": 1000}

pipe.run()
```

**Terminal Output Example:**

```text
  ▶  Clean Dataset...
     💬 "The pipeline removed 45 invalid rows and imputed missing values in 1.2s."
  ✅  Done
```
