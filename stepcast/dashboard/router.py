from __future__ import annotations

from typing import Any

try:
    from fastapi import APIRouter, Depends, Query  # noqa: F401
    from fastapi.responses import JSONResponse  # noqa: F401
except ImportError:
    pass

from stepcast.dashboard.storage import RunStorage


def create_router(storage: RunStorage) -> Any:  # noqa: ANN401
    """Create and return the FastAPI APIRouter for dashboard REST endpoints.

    Args:
        storage: RunStorage instance to query.

    Returns:
        Configured APIRouter.
    """
    from fastapi import APIRouter, Query

    router = APIRouter()

    @router.get("/api/runs")
    async def list_runs(
        limit: int = Query(50, ge=1, le=500),
        status: str | None = Query(None),
        pipeline_name: str | None = Query(None),
    ) -> Any:  # noqa: ANN401
        """List recent pipeline runs with optional filters."""
        return storage.list_runs(
            limit=limit, status=status, pipeline_name=pipeline_name
        )

    @router.get("/api/runs/{run_id}")
    async def get_run(run_id: str) -> Any:  # noqa: ANN401
        """Get the full details of a specific run."""
        from fastapi import HTTPException

        data = storage.get_run(run_id)
        if data is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return data

    @router.delete("/api/runs/{run_id}")
    async def delete_run(run_id: str) -> Any:  # noqa: ANN401
        """Delete a specific run."""
        from fastapi import HTTPException

        deleted = storage.delete_run(run_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Run not found")
        return {"deleted": True}

    @router.get("/api/stats")
    async def get_stats() -> Any:  # noqa: ANN401
        """Get aggregate run statistics."""
        return storage.stats()

    return router
