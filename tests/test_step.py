"""Tests for @step decorator and StepDefinition."""
from __future__ import annotations

import time

from stepcast import Pipeline


def test_step_retries_on_failure() -> None:
    """Step retries the configured number of times."""
    attempts = []
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Flaky", retries=2, retry_delay=0)
    def flaky() -> None:
        attempts.append(1)
        if len(attempts) < 3:
            raise OSError("transient")

    report = pipe.run()

    assert report.success is True
    assert len(attempts) == 3
    assert report.steps[0].retries_used == 2


def test_step_fails_after_all_retries() -> None:
    """Step is marked failed after exhausting retries."""
    pipe = Pipeline("Test", fail_fast=False, show_summary=False)

    @pipe.step("Always fails", retries=2, retry_delay=0)
    def bad() -> None:
        raise RuntimeError("nope")

    report = pipe.run()

    assert report.steps[0].status == "failed"
    assert report.steps[0].retries_used == 2


def test_step_timeout() -> None:
    """Step that exceeds timeout is marked failed."""
    pipe = Pipeline("Test", fail_fast=False, show_summary=False)

    @pipe.step("Slow", timeout=0.1)
    def slow() -> None:
        time.sleep(10)

    report = pipe.run()

    assert report.steps[0].status == "failed"


def test_step_tags() -> None:
    """Step tags are stored in StepResult."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Tagged", tags=["etl", "smoke"])
    def tagged() -> None:
        pass

    report = pipe.run()

    assert "etl" in report.steps[0].tags
    assert "smoke" in report.steps[0].tags


def test_step_no_args_func() -> None:
    """Step function with no args is called without prev_output."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("No args")
    def no_args() -> int:
        return 7

    report = pipe.run()
    assert report.steps[0].output == 7


def test_step_chaining() -> None:
    """Each step receives the output of the previous step."""
    pipe = Pipeline("Test", show_summary=False)

    @pipe.step("Produce")
    def produce() -> list[int]:
        return [1, 2, 3]

    @pipe.step("Transform")
    def transform(data: list[int]) -> int:
        return sum(data)

    report = pipe.run()
    assert report.steps[1].output == 6
