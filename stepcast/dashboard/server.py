from __future__ import annotations

import asyncio
import threading
import webbrowser
from pathlib import Path
from typing import Any

STATIC_DIR = Path(__file__).parent / "static"


def create_app(storage: Any) -> Any:  # noqa: ANN401
    """Create and return the FastAPI application.

    Args:
        storage: RunStorage instance.

    Returns:
        Configured FastAPI app.
    """
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles

    from stepcast.dashboard.router import create_router
    from stepcast.dashboard.ws import ConnectionManager

    app = FastAPI(title="stepcast dashboard", docs_url=None, redoc_url=None)
    manager = ConnectionManager()

    @app.get("/")
    async def index() -> HTMLResponse:
        return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.websocket("/ws/live/{run_id}")
    async def live_stream(websocket: WebSocket, run_id: str) -> None:
        """WebSocket endpoint — clients subscribe to a run_id for live events."""
        await manager.connect(websocket, run_id)
        try:
            while True:
                await asyncio.sleep(30)  # keepalive ping interval
        except WebSocketDisconnect:
            manager.disconnect(websocket, run_id)

    # Attach REST routes
    api_router = create_router(storage)
    app.include_router(api_router)

    # Serve static files (JS, CSS)
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Store manager for external use (e.g. pipeline broadcasting)
    app.state.manager = manager
    app.state.storage = storage

    return app


def serve(
    host: str = "127.0.0.1",
    port: int = 4321,
    open_browser: bool = True,
) -> None:
    """Launch the local stepcast dashboard (Model A).

    Args:
        host: Bind host (default 127.0.0.1 — localhost only).
        port: Bind port (default 4321).
        open_browser: Open the default browser automatically.
    """
    import uvicorn

    from stepcast.dashboard.storage import RunStorage

    storage = RunStorage()
    app = create_app(storage)

    if open_browser:
        url = f"http://{host}:{port}"
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    uvicorn.run(app, host=host, port=port, log_level="warning")
