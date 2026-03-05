"""Tests for the sync Runner."""
from __future__ import annotations

from stepcast.display import Renderer
from stepcast.runner import Runner
from stepcast.step import StepDefinition


def _make_runner() -> Runner:
    return Runner(Renderer())


def test_runner_passes_output_to_next() -> None:
    """Runner passes the output of one step to the next."""
    runner = _make_runner()

    step1 = StepDefinition(fn=lambda: 42, label="Step 1")
    step2 = StepDefinition(fn=lambda x: x + 1, label="Step 2")

    r1 = runner.run_step(step1, None)
    r2 = runner.run_step(step2, r1.output)

    assert r1.output == 42
    assert r2.output == 43


def test_runner_captures_exception() -> None:
    """Runner captures exception and marks step as failed."""

    def bad() -> None:
        raise ValueError("test error")

    runner = _make_runner()
    step = StepDefinition(fn=bad, label="Bad Step")
    result = runner.run_step(step, None)

    assert result.status == "failed"
    assert isinstance(result.error, ValueError)


def test_runner_skip_if_true() -> None:
    """Step is skipped when skip_if returns True."""
    called = []
    runner = _make_runner()
    step = StepDefinition(
        fn=lambda: called.append(1),
        label="Maybe Skip",
        skip_if=lambda: True,
    )
    result = runner.run_step(step, None)

    assert result.status == "skipped"
    assert called == []


def test_runner_retry_succeeds() -> None:
    """Runner retries and eventually succeeds."""
    attempts = []

    def flaky() -> int:
        attempts.append(1)
        if len(attempts) < 2:
            raise OSError("transient")
        return 99

    runner = _make_runner()
    step = StepDefinition(fn=flaky, label="Flaky", retries=2, retry_delay=0)
    result = runner.run_step(step, None)

    assert result.status == "passed"
    assert result.output == 99
    assert len(attempts) == 2
