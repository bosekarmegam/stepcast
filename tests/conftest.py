"""Shared pytest fixtures for stepcast tests."""
from __future__ import annotations

import pytest

from stepcast import Pipeline
from stepcast.display import Renderer
from stepcast.models import RunReport, StepResult


@pytest.fixture
def simple_pipeline() -> Pipeline:
    """Return a fresh Pipeline with show_summary=False for clean test output."""
    return Pipeline("Test Pipeline", show_summary=False)


@pytest.fixture
def renderer() -> Renderer:
    """Return a plain Renderer instance."""
    return Renderer()


@pytest.fixture
def passing_report() -> RunReport:
    """Return a minimal passing RunReport."""
    return RunReport(
        pipeline_name="Test",
        success=True,
        total_time=1.0,
        steps=[
            StepResult(label="Step A", status="passed", duration=0.5),
            StepResult(label="Step B", status="passed", duration=0.5),
        ],
    )


@pytest.fixture
def failing_report() -> RunReport:
    """Return a minimal failing RunReport."""
    return RunReport(
        pipeline_name="Test",
        success=False,
        total_time=1.0,
        steps=[
            StepResult(label="Step A", status="passed", duration=0.5),
            StepResult(
                label="Step B",
                status="failed",
                duration=0.5,
                error=ValueError("boom"),
            ),
        ],
    )
