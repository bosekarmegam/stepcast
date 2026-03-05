"""Tests for the terminal Renderer."""
from __future__ import annotations

import io
import sys

from stepcast.display import Renderer
from stepcast.models import RunReport, StepResult


def _capture(fn):  # noqa: ANN001, ANN202
    """Capture stdout from a function call."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn()
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_renderer_header() -> None:
    r = Renderer()
    out = _capture(lambda: r.print_header("My Pipeline"))
    assert "My Pipeline" in out


def test_renderer_step_passed() -> None:
    r = Renderer()
    result = StepResult(label="Step A", status="passed", duration=0.42)
    out = _capture(lambda: r.print_step_done(result))
    assert "0.4s" in out


def test_renderer_step_failed() -> None:
    r = Renderer()
    result = StepResult(
        label="Step A",
        status="failed",
        duration=1.0,
        error=ValueError("boom"),
    )
    out = _capture(lambda: r.print_step_done(result))
    assert "Failed" in out or "FAIL" in out


def test_renderer_skipped() -> None:
    r = Renderer()
    result = StepResult(label="Step A", status="skipped", duration=0.0)
    out = _capture(lambda: r.print_step_done(result))
    assert "Skip" in out or "SKIP" in out or "skip" in out


def test_renderer_summary_passed(passing_report: RunReport) -> None:
    r = Renderer()
    out = _capture(lambda: r.print_summary(passing_report))
    assert "2" in out


def test_renderer_stdout_line() -> None:
    r = Renderer()
    out = _capture(lambda: r.print_stdout_line("hello world"))
    assert "hello world" in out
