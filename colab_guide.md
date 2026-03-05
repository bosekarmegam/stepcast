# Google Colab Integration

`stepcast` works seamlessly inside Google Colab notebooks, providing beautiful output and built-in Google Drive integration for saving your run reports.

## Installation

To use `stepcast` in Colab, install it with the `[colab]` extras:

```python
!pip install "stepcast[colab]"
```

This ensures the necessary Google authentication libraries are available.

## Authorizing Google Drive

If you want to save your pipeline run reports directly to your Google Drive, you first need to authenticate `stepcast`.

```python
from stepcast.integrations import colab

# This will open a standard Colab OAuth popup requesting access to Drive
colab.auth()
```

> **Note:** This authentication only requests access to Google Drive (the `drive.file` scope) and is required if you use the `save_to_drive` feature. It is not necessary if you just want to run pipelines and view the terminal output.

## Saving Runs to Drive

Once authenticated, you can save any `RunReport` directly to your Drive:

```python
from stepcast import Pipeline
from stepcast.integrations import colab

pipe = Pipeline("My Colab Pipeline")

@pipe.step("Process Data")
def process():
    print("Crunching numbers...")
    return 42

# Run the pipeline to get the report
report = pipe.run()

# Save the report JSON to Drive
# It defaults to the 'stepcast/runs' folder in your Drive.
saved_path = colab.save_to_drive(report)
print(f"Saved to: {saved_path}")
```

You can optionally specify a custom folder when saving:

```python
colab.save_to_drive(report, folder="my_project/pipeline_logs")
```

## Future Sharing Features

In a future update, `stepcast` will support publishing pipelines directly to Colab as shareable URLs via Gist integration. This feature is currently a stub (`colab.publish_to_colab()`) but will be expanded soon!
