# API Reference

## `Pipeline`

```python
from stepcast import Pipeline

pipe = Pipeline(
    name="My Pipeline",       # str — shown in header (required)
    fail_fast=True,           # bool — abort on first failure
    narrate=False,            # bool — Gemini AI narration
    rich=None,                # bool|None — None = auto-detect
    log_file=None,            # str|Path|None — save JSON report
    show_summary=True,        # bool — print final summary
    timezone="UTC",           # str — timezone for timestamps
    dashboard=False,          # bool|str — stream to dashboard
)
```

---

## `@pipe.step()`

```python
@pipe.step(
    label="Human-readable step name",   # str (required)
    retries=0,                           # int — retry count
    retry_delay=1.0,                     # float — secs (exp backoff)
    skip_if=None,                        # callable → bool
    timeout=None,                        # float|None — seconds
    tags=[],                             # list[str]
    capture_output=True,                 # bool — stream stdout
)
def my_step(prev_result):
    ...
    return result
```

---

## `pipe.run()`

```python
report = pipe.run(
    initial=None,      # Any — passed to first step
    steps=None,        # list[str]|None — filter by label or tag
    dry_run=False,     # bool — print steps without executing
)
```

Raises `PipelineAbortError` if `fail_fast=True` and a step fails.

---

## `RunReport`

```python
report.success              # bool
report.total_time           # float (seconds)
report.steps                # list[StepResult]
report.pipeline_name        # str
report.timestamp            # datetime
report.to_json()            # dict
report.to_file("run.json")  # save JSON
report.summary()            # one-line str
report.failed_steps()       # list[StepResult]
report.passed_steps()       # list[StepResult]
```

---

## `StepResult`

```python
result.label           # str
result.status          # "passed" | "failed" | "skipped"
result.duration        # float
result.output          # Any
result.stdout          # str
result.error           # Exception | None
result.narration       # str | None
result.retries_used    # int
result.tags            # list[str]
result.timestamp       # datetime
```

---

## Exceptions

```python
from stepcast import StepFailedError, PipelineAbortError

# StepFailedError — step failed after retries
# PipelineAbortError — pipeline aborted (fail_fast=True)
```

---

## CLI Commands

```bash
stepcast version                             # Print version
stepcast doctor                              # Environment check
stepcast config set gemini_api_key KEY       # Set config
stepcast config get gemini_api_key           # Get config
stepcast serve                               # Launch dashboard
stepcast run pipeline_script.py             # Run a script
stepcast check                               # Validate config
```
