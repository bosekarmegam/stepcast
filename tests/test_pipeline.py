"""Tests for Pipeline class."""
from __future__ import annotations

import pytest

from stepcast import Pipeline
from stepcast.exceptions import PipelineAbortError


def test_pipeline_basic_run() -> None:
    """Pipeline with two steps succeeds and returns RunReport."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("First step")
    def step1() -> int:
        return 42

    @pipe.step("Second step")
    def step2(val: int) -> int:
        return val + 1

    report = pipe.run()

    assert report.success is True
    assert len(report.steps) == 2
    assert report.steps[0].status == "passed"
    assert report.steps[1].status == "passed"
    assert report.steps[1].output == 43


def test_pipeline_fail_fast() -> None:
    """Pipeline with fail_fast=True raises PipelineAbortError on first failure."""
    pipe = Pipeline("Test", fail_fast=True, show_summary=False)

    @pipe.step("Failing step")
    def step1() -> None:
        raise ValueError("oops")

    @pipe.step("Should not run")
    def step2() -> None:
        pass

    with pytest.raises(PipelineAbortError) as exc_info:
        pipe.run()

    assert "Test" in str(exc_info.value)
    assert len(pipe.last_run.steps) == 1  # type: ignore[union-attr]


def test_pipeline_no_fail_fast() -> None:
    """Pipeline with fail_fast=False continues after failure."""
    pipe = Pipeline("Test", fail_fast=False, show_summary=False)

    @pipe.step("Failing step")
    def step1() -> None:
        raise ValueError("oops")

    @pipe.step("Continuing")
    def step2(val: None) -> str:
        return "ran"

    report = pipe.run()

    assert report.success is False
    assert len(report.steps) == 2
    assert report.steps[0].status == "failed"
    assert report.steps[1].status == "passed"


def test_pipeline_skip_if() -> None:
    """Step with skip_if returning True is skipped."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Skipped step", skip_if=lambda: True)
    def step1() -> int:
        return 999

    report = pipe.run()

    assert report.steps[0].status == "skipped"
    assert report.success is True


def test_pipeline_dry_run() -> None:
    """Dry run does not execute steps."""
    called = []
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Never runs")
    def step1() -> None:
        called.append(True)

    report = pipe.run(dry_run=True)

    assert called == []
    assert report.steps[0].status == "skipped"


def test_pipeline_initial_value() -> None:
    """Initial value is passed to first step."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Receives initial")
    def step1(val: int) -> int:
        return val * 2

    report = pipe.run(initial=10)

    assert report.steps[0].output == 20


def test_pipeline_step_filter_by_label() -> None:
    """steps= parameter filters by label."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Step A")
    def a() -> str:
        return "a"

    @pipe.step("Step B")
    def b() -> str:
        return "b"

    report = pipe.run(steps=["Step A"])

    assert len(report.steps) == 1
    assert report.steps[0].label == "Step A"


@pytest.mark.smoke
def test_smoke_end_to_end() -> None:
    """Minimal end-to-end: 3 steps pass, report.success is True."""
    pipe = Pipeline("Smoke", show_summary=False)

    @pipe.step("One")
    def one() -> int:
        return 1

    @pipe.step("Two")
    def two(x: int) -> int:
        return x + 1

    @pipe.step("Three")
    def three(x: int) -> int:
        return x + 1

    report = pipe.run()
    assert report.success
    assert len(report.steps) == 3
    assert report.steps[2].output == 3
