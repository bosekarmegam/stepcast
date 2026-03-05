from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def fmt_time(seconds: float) -> str:
    """Format a duration into a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string: '0.4s', '1.2s', '12s', '2m 4s'.

    Example:
        >>> fmt_time(0.42)
        '0.4s'
        >>> fmt_time(65)
        '1m 5s'
    """
    if seconds < 1:
        return f"{seconds:.1f}s"
    if seconds < 10:
        return f"{seconds:.1f}s"
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"


def terminal_supports_unicode() -> bool:
    """Detect whether the current terminal supports Unicode output.

    Returns:
        True if the terminal encoding supports Unicode characters.

    Example:
        >>> isinstance(terminal_supports_unicode(), bool)
        True
    """
    encoding = getattr(sys.stdout, "encoding", None) or ""
    return encoding.lower().replace("-", "") in (
        "utf8",
        "utf16",
        "utf32",
        "utf8bom",
    )


_SECRET_PATTERNS: list[str] = [
    r"(?i)(api[_\-]?key|token|password|secret|auth)[=:\s]\S+",
    r"(?i)(bearer|basic)\s+\S+",
    r"AIza[0-9A-Za-z\-_]{35}",   # Google API key pattern
]

_COMPILED_PATTERNS = [re.compile(p) for p in _SECRET_PATTERNS]


def scrub_stdout(text: str) -> str:
    """Remove secrets and sensitive tokens from captured stdout.

    Args:
        text: Raw captured output from a step.

    Returns:
        Scrubbed text with secrets replaced by [REDACTED].

    Example:
        >>> scrub_stdout("api_key=supersecret123")
        'api_key=[REDACTED]'
    """
    for pattern in _COMPILED_PATTERNS:
        text = pattern.sub(
            lambda m: m.group(0).split("=")[0] + "=[REDACTED]"
            if "=" in m.group(0)
            else "[REDACTED]",
            text,
        )
    return text


def safe_filename(user_input: str) -> str:
    """Sanitise a user-supplied string for safe use in file paths.

    Args:
        user_input: Arbitrary user string.

    Returns:
        String with only word chars, hyphens, underscores, and dots.

    Example:
        >>> safe_filename("../../etc/passwd")
        '______etc_passwd'
    """
    return re.sub(r"[^\w\-_.]", "_", user_input)


def detect_platform() -> str:
    """Return a human-readable platform string.

    Returns:
        Platform description string.
    """
    import platform

    system = platform.system()
    machine = platform.machine()
    version = platform.version()
    if system == "Darwin":
        mac_ver = platform.mac_ver()[0]
        return f"macOS {mac_ver} ({machine})"
    if system == "Windows":
        return f"Windows {version} ({machine})"
    return f"Linux {version} ({machine})"


def truncate_line(line: str, max_length: int = 200) -> str:
    """Truncate a line to max_length, appending '…' if truncated.

    Args:
        line: The line to truncate.
        max_length: Maximum allowed length (default 200).

    Returns:
        Truncated line.
    """
    if len(line) > max_length:
        return line[:max_length] + "…"
    return line


def load_json_file(path: Path) -> dict[str, object]:
    """Load and parse a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed dictionary.

    Raises:
        FileNotFoundError: If file does not exist.
        json.JSONDecodeError: If file is not valid JSON.
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]
