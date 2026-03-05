from __future__ import annotations

import contextlib
import json
import locale
import os
from pathlib import Path
from typing import Any

_LOCALES_DIR = Path(__file__).parent / "locales"
_cache: dict[str, dict[str, str]] = {}


def _load_locale(lang: str) -> dict[str, str]:
    """Load locale data from the locales directory.

    Args:
        lang: Locale code (e.g. 'en', 'es').

    Returns:
        Dictionary mapping keys to translated strings.
    """
    if lang in _cache:
        return _cache[lang]
    locale_file = _LOCALES_DIR / f"{lang}.json"
    if locale_file.exists():
        with open(locale_file, encoding="utf-8") as f:
            data: dict[str, str] = json.load(f)
        _cache[lang] = data
        return data
    return {}


def _detect_locale() -> str:
    """Detect the best available locale in priority order.

    Priority:
        1. STEPCAST_LOCALE env var
        2. LANG env var (first two chars)
        3. System locale
        4. 'en' fallback

    Returns:
        Locale code string.
    """
    if lang := os.getenv("STEPCAST_LOCALE"):
        return lang.split("_")[0].lower()
    if lang := os.getenv("LANG"):
        return lang.split("_")[0].lower()
    try:
        sys_lang = locale.getpreferredencoding(False)
        if sys_lang and sys_lang != "ANSI_X3.4-1968":
            return sys_lang[:2].lower()
    except Exception:
        pass
    return "en"


def t(key: str, **kwargs: Any) -> str:  # noqa: ANN401
    """Look up a localised string by key and format it with kwargs.

    Falls back to English if the key is not found in the current locale.
    Falls back to the raw key string if not found in English either.

    Args:
        key: Dotted key string (e.g. 'step.passed').
        **kwargs: Format arguments to substitute into the string.

    Returns:
        Formatted translated string.

    Example:
        >>> t('step.passed', duration='0.4s')
        '✅  Done  (0.4s)'
    """
    lang = _detect_locale()
    translations = _load_locale(lang)
    text = translations.get(key)

    if text is None and lang != "en":
        en = _load_locale("en")
        text = en.get(key)

    if text is None:
        text = key

    if kwargs:
        with contextlib.suppress(KeyError, ValueError):
            text = text.format(**kwargs)

    return text
