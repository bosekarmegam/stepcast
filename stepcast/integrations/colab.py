from __future__ import annotations

from typing import Any


def auth() -> None:
    """Authenticate with Google for Drive access (Colab only).

    Opens an OAuth popup requesting the drive.file scope.
    Must be called inside a Google Colab notebook.

    Raises:
        ImportError: If google-auth dependencies are not installed.
        RuntimeError: If not running inside Google Colab.
    """
    import sys

    if "google.colab" not in sys.modules:
        raise RuntimeError("auth() must be called inside a Google Colab notebook")

    try:
        from google.colab import auth as _colab_auth

        _colab_auth.authenticate_user()
    except ImportError as exc:
        raise ImportError(
            "Install Colab dependencies: pip install 'stepcast[colab]'"
        ) from exc


def save_to_drive(report: Any, folder: str = "stepcast/runs") -> str:  # noqa: ANN401
    """Save a RunReport JSON to Google Drive.

    Args:
        report: A RunReport instance or dict.
        folder: Drive folder path relative to My Drive (default 'stepcast/runs').

    Returns:
        Path string where the file was saved.

    Raises:
        ImportError: If google-auth dependencies are not installed.
    """
    import sys
    from datetime import datetime

    if "google.colab" not in sys.modules:
        raise RuntimeError("save_to_drive() must be called inside a Google Colab notebook")  # noqa: E501

    try:  # noqa: SIM105
        import gdown  # noqa: F401
    except ImportError:
        pass

    data = report.to_json() if hasattr(report, "to_json") else report
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{ts}.json"

    # Mount Drive and write file
    try:
        from google.colab import drive

        drive.mount("/content/drive")
        import json
        from pathlib import Path

        target_dir = Path(f"/content/drive/MyDrive/{folder}")
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(target_path)
    except ImportError as exc:
        raise ImportError(
            "Install Colab dependencies: pip install 'stepcast[colab]'"
        ) from exc


def publish_to_colab(script_path: str) -> str:
    """Generate a shareable Colab URL for a pipeline script.

    Args:
        script_path: Local path to the .py pipeline script.

    Returns:
        Shareable Colab URL string.
    """
    # This is a stub — full implementation would upload to Gist and
    # generate a colab.research.google.com/gist/... URL
    return f"https://colab.research.google.com  (Upload {script_path} manually)"
