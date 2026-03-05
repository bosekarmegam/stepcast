"""Tests for RunReport and StepResult models."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from stepcast.models import RunReport, StepResult


def test_step_result_to_json() -> None:
    result = StepResult(label="A", status="passed", duration=1.5, output=42)
    data = result.to_json()
    assert data["label"] == "A"
    assert data["status"] == "passed"
    assert data["duration"] == 1.5
    assert "timestamp" in data


def test_run_report_summary_passed(passing_report: RunReport) -> None:
    summary = passing_report.summary()
    assert "passed" in summary


def test_run_report_summary_failed(failing_report: RunReport) -> None:
    summary = failing_report.summary()
    assert "failed" in summary


def test_run_report_to_json(passing_report: RunReport) -> None:
    data = passing_report.to_json()
    assert data["success"] is True
    assert len(data["steps"]) == 2
    # Verify it's round-trippable
    json_str = json.dumps(data)
    loaded = json.loads(json_str)
    assert loaded["pipeline_name"] == "Test"


def test_run_report_to_file(passing_report: RunReport) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "run.json"
        passing_report.to_file(str(path))
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["success"] is True


def test_run_report_failed_steps(failing_report: RunReport) -> None:
    assert len(failing_report.failed_steps()) == 1
    assert failing_report.failed_steps()[0].label == "Step B"


def test_run_report_passed_steps(failing_report: RunReport) -> None:
    assert len(failing_report.passed_steps()) == 1
    assert failing_report.passed_steps()[0].label == "Step A"
