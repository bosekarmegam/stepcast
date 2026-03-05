"""Integration tests for Rich renderer (mocked)."""
from __future__ import annotations

import pytest


@pytest.mark.integration
def test_rich_renderer_falls_back_gracefully() -> None:
    """RichRenderer works even when rich is not installed."""
    from unittest.mock import patch

    with patch.dict("sys.modules", {"rich": None, "rich.console": None}):
        from stepcast.integrations.rich_display import RichRenderer

        r = RichRenderer()
        assert r._console is None  # Fell back to plain
