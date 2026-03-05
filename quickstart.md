# Quickstart

## Install

```bash
pip install stepcast
```

## Your First Pipeline

```python
from stepcast import Pipeline

pipe = Pipeline("My Pipeline")

@pipe.step("Download data", retries=2)
def download():
    print("Fetching...")
    return [1, 2, 3]

@pipe.step("Process data")
def process(data: list):
    result = sum(data)
    print(f"Sum = {result}")
    return result

report = pipe.run()
print(report.summary())
```

## Key Options

| Option | Default | Description |
|--------|---------|-------------|
| `fail_fast` | `True` | Abort on first failure |
| `narrate` | `False` | Gemini AI narration (needs API key) |
| `rich` | auto | Use rich library if available |
| `log_file` | `None` | Save JSON report to file |
| `dashboard` | `False` | Stream to local dashboard |

## Install Optional Features

```bash
pip install "stepcast[rich]"        # Beautiful output
pip install "stepcast[dashboard]"   # Web dashboard
pip install "stepcast[gemini]"      # AI narration
pip install "stepcast[all]"         # Everything
```

## Next Steps

- [API Reference](api_reference.md)
- [Dashboard Guide](dashboard.md)
- [Gemini Narration](gemini_narration.md)
