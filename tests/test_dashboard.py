"""Tests for the stepcast dashboard (FastAPI + SQLite)."""
from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient

    from stepcast.dashboard.server import create_app
    from stepcast.dashboard.storage import RunStorage

    HAS_DASHBOARD = True
except ImportError:
    HAS_DASHBOARD = False


@pytest.mark.dashboard
@pytest.mark.skipif(not HAS_DASHBOARD, reason="dashboard deps not installed")
class TestDashboard:
    """Integration tests for the dashboard API."""

    @pytest.fixture
    def client(self):  # noqa: ANN201
        storage = RunStorage(":memory:")
        app = create_app(storage)
        return TestClient(app), storage

    def test_health(self, client) -> None:  # noqa: ANN001
        c, _ = client
        resp = c.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_list_runs_empty(self, client) -> None:  # noqa: ANN001
        c, _ = client
        resp = c.get("/api/runs")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_save_and_list_run(self, client) -> None:  # noqa: ANN001
        c, storage = client
        storage.save_run(
            {
                "pipeline_name": "Test Pipeline",
                "success": True,
                "total_time": 1.5,
                "timestamp": "2026-01-01T00:00:00",
                "steps": [],
            }
        )
        resp = c.get("/api/runs")
        assert resp.status_code == 200
        runs = resp.json()
        assert len(runs) == 1
        assert runs[0]["pipeline_name"] == "Test Pipeline"

    def test_get_run_detail(self, client) -> None:  # noqa: ANN001
        c, storage = client
        payload = {
            "pipeline_name": "Detail Test",
            "success": False,
            "total_time": 2.0,
            "timestamp": "2026-01-01T00:00:00",
            "steps": [{"label": "Step A", "status": "failed"}],
        }
        run_id = storage.save_run(payload)
        resp = c.get(f"/api/runs/{run_id}")
        assert resp.status_code == 200
        assert resp.json()["pipeline_name"] == "Detail Test"

    def test_get_run_not_found(self, client) -> None:  # noqa: ANN001
        c, _ = client
        resp = c.get("/api/runs/nonexistent-id")
        assert resp.status_code == 404

    def test_stats_endpoint(self, client) -> None:  # noqa: ANN001
        c, storage = client
        storage.save_run(
            {
                "pipeline_name": "P",
                "success": True,
                "total_time": 1.0,
                "timestamp": "2026-01-01T00:00:00",
                "steps": [],
            }
        )
        resp = c.get("/api/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total"] == 1
        assert stats["passed"] == 1
        assert stats["failed"] == 0

    def test_filter_by_status(self, client) -> None:  # noqa: ANN001
        c, storage = client
        storage.save_run(
            {
                "pipeline_name": "P1",
                "success": True,
                "total_time": 1.0,
                "timestamp": "2026-01-01T00:00:00",
                "steps": [],
            }
        )
        storage.save_run(
            {
                "pipeline_name": "P2",
                "success": False,
                "total_time": 2.0,
                "timestamp": "2026-01-01T00:00:00",
                "steps": [],
            }
        )
        resp = c.get("/api/runs?status=passed")
        assert len(resp.json()) == 1
        assert resp.json()[0]["pipeline_name"] == "P1"
