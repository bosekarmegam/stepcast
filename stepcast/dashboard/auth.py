from __future__ import annotations

import os
from typing import Any

try:
    from fastapi import HTTPException, Request  # noqa: F401
    from fastapi.security import HTTPBearer  # noqa: F401
except ImportError:
    pass


def get_auth_key() -> str | None:
    """Return the configured team server auth key.

    Returns:
        Auth key string or None if not configured.
    """
    return os.getenv("STEPCAST_AUTH_KEY")


async def verify_auth(request: Any) -> None:  # noqa: ANN401
    """Middleware: verify the Bearer token for Model B team auth.

    Does nothing (allows all) if STEPCAST_AUTH_KEY is not set (Model A local mode).

    Args:
        request: FastAPI Request object.

    Raises:
        HTTPException: 401 if auth key is set but token doesn't match.
    """
    expected = get_auth_key()
    if not expected:
        return  # Model A: no auth required

    from fastapi import HTTPException

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = auth_header.removeprefix("Bearer ").strip()
    if token != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")
