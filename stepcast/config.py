from __future__ import annotations

import os
import stat
import sys
from pathlib import Path
from typing import Any

CONFIG_PATH = Path.home() / ".stepcast" / "config.toml"


def _load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML file using the stdlib or tomli fallback.

    Args:
        path: Path to TOML file.

    Returns:
        Parsed configuration dictionary.
    """
    if sys.version_info >= (3, 11):
        import tomllib

        with open(path, "rb") as f:
            return tomllib.load(f)  # type: ignore[no-any-return]
    else:
        try:
            import tomllib

            with open(path, "rb") as f:
                return tomllib.load(f)  # type: ignore[no-any-return]
        except ImportError:
            try:
                import tomli as tomllib

                with open(path, "rb") as f:
                    return tomllib.load(f)  # type: ignore[no-any-return]
            except ImportError:
                # Minimal TOML parser fallback (key = "value" only)
                return _parse_simple_toml(path)


def _parse_simple_toml(path: Path) -> dict[str, Any]:
    """Very minimal TOML parser for simple key = "value" files.

    Args:
        path: Path to simple TOML file.

    Returns:
        Parsed dictionary.
    """
    result: dict[str, Any] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                result[key] = value
    return result


def get_config() -> dict[str, Any]:
    """Load the full user config from ~/.stepcast/config.toml.

    Returns:
        Configuration dictionary (empty dict if file does not exist).
    """
    if CONFIG_PATH.exists():
        try:
            return _load_toml(CONFIG_PATH)
        except Exception:
            return {}
    return {}


def get_gemini_api_key() -> str | None:
    """Resolve the Gemini API key from env vars or config file.

    Priority:
        1. STEPCAST_GEMINI_API_KEY env var (highest priority)
        2. GEMINI_API_KEY env var (fallback for users who set this)
        3. ~/.stepcast/config.toml  gemini_api_key field
        4. None — caller must handle gracefully, never crash

    Returns:
        API key string or None.
    """
    key = os.getenv("STEPCAST_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key:
        return key
    cfg = get_config()
    return cfg.get("gemini_api_key")


def get_server_url() -> str | None:
    """Get configured team server URL.

    Returns:
        Server URL or None.
    """
    return os.getenv("STEPCAST_SERVER_URL") or get_config().get("server_url")


def get_server_key() -> str | None:
    """Get configured team server API key.

    Returns:
        Server API key or None.
    """
    return os.getenv("STEPCAST_AUTH_KEY") or get_config().get("server_key")


def set_config(key: str, value: str) -> None:
    """Write a key-value pair to ~/.stepcast/config.toml.

    Creates the config file and directory if they don't exist.
    Sets file permissions to 600 (owner read/write only) on POSIX systems.

    Args:
        key: Config key to set.
        value: Value to assign.
    """
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config
    existing: dict[str, Any] = {}
    if CONFIG_PATH.exists():
        try:
            existing = _load_toml(CONFIG_PATH)
        except Exception:
            existing = {}

    existing[key] = value

    # Write back as a simple TOML file
    lines = ["# stepcast user config — do not commit this file\n"]
    for k, v in existing.items():
        lines.append(f'{k} = "{v}"\n')

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Set restrictive permissions on POSIX (Linux/macOS)
    if os.name == "posix":
        CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)


def get_config_value(key: str) -> str | None:
    """Read a single value from the config file.

    Args:
        key: Config key to read.

    Returns:
        Value string or None if not set.
    """
    return get_config().get(key)
