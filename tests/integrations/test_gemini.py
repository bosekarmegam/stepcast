"""Integration tests for Gemini narration (mocked — no real API calls)."""
from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.mark.integration
def test_narrate_step_no_key() -> None:
    """narrate_step returns None when no API key is configured."""
    with patch("stepcast.config.get_gemini_api_key", return_value=None):
        from stepcast.integrations.gemini import narrate_step

        result = narrate_step("Step A", "output", 1.0, "result")
    assert result is None


@pytest.mark.integration
def test_narrate_step_with_key() -> None:
    """narrate_step returns None when google.generativeai import fails gracefully."""
    # We can't easily mock google.generativeai in the test environment,
    # but we CAN verify that when the key IS set, the function attempts
    # the call and returns None on ImportError (since we don't have the real SDK).
    with patch("stepcast.config.get_gemini_api_key", return_value="fake-key"):
        from stepcast.integrations.gemini import narrate_step

        result = narrate_step("Step A", "→ 42 rows", 0.5, "[1, 2, 3]")
    # Without google-generativeai installed, it should silently return None
    assert result is None


@pytest.mark.integration
def test_narrate_step_exception_is_silent() -> None:
    """narrate_step swallows any exception and returns None."""
    with patch("stepcast.config.get_gemini_api_key", return_value="fake-key"):  # noqa: SIM117
        with patch.dict("sys.modules", {"google.generativeai": None}):
            from stepcast.integrations.gemini import narrate_step

            result = narrate_step("Step A", "output", 1.0, "result")
    assert result is None
