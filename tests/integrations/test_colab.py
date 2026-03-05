"""Integration tests for Colab module (mocked)."""
from __future__ import annotations

import pytest


@pytest.mark.integration
def test_auth_raises_outside_colab() -> None:
    """auth() raises RuntimeError outside Google Colab."""
    from stepcast.integrations.colab import auth

    with pytest.raises(RuntimeError, match="Colab"):
        auth()


@pytest.mark.integration
def test_save_to_drive_raises_outside_colab() -> None:
    """save_to_drive() raises RuntimeError outside Google Colab."""
    from stepcast.integrations.colab import save_to_drive

    with pytest.raises(RuntimeError, match="Colab"):
        save_to_drive({})
