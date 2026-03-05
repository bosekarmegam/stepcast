from __future__ import annotations

from typing import Any

try:
    from fastapi import WebSocket
except ImportError:
    WebSocket = Any  # type: ignore[assignment,misc]


class ConnectionManager:
    """Manages active WebSocket connections per pipeline run.

    Example:
        >>> manager = ConnectionManager()
        >>> await manager.connect(websocket, run_id="abc123")
        >>> await manager.broadcast("abc123", {"event": "step_done"})
    """

    def __init__(self) -> None:
        # Maps run_id -> list of connected WebSocket clients
        self._connections: dict[str, list[Any]] = {}

    async def connect(self, websocket: Any, run_id: str) -> None:  # noqa: ANN401
        """Accept and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance.
            run_id: Pipeline run identifier to subscribe to.
        """
        await websocket.accept()
        self._connections.setdefault(run_id, []).append(websocket)

    def disconnect(self, websocket: Any, run_id: str) -> None:  # noqa: ANN401
        """Remove a WebSocket from the active connections.

        Args:
            websocket: WebSocket to remove.
            run_id: Run identifier it was subscribed to.
        """
        conns = self._connections.get(run_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, run_id: str, event: dict[str, Any]) -> None:
        """Send a JSON event to all clients subscribed to a run.

        Args:
            run_id: Target run identifier.
            event: JSON-serialisable event dict.
        """
        import json

        conns = self._connections.get(run_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_text(json.dumps(event))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, run_id)
