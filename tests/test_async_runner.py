"""Tests for the async runner."""
import asyncio
from typing import NoReturn

import pytest

from stepcast.display import Renderer
from stepcast.models import RunReport, StepResult
from stepcast.runner import AsyncRunner
from stepcast.step import StepDefinition


class DummyRenderer(Renderer):
    def print_header(self, name: str) -> None: pass
    def print_step_start(self, name: str) -> None: pass
    def print_step_done(self, result: StepResult) -> None: pass
    def print_stdout_line(self, line: str) -> None: pass
    def print_summary(self, report: RunReport) -> None: pass
    def print_retry(self, attempt: int, mx: int) -> None: pass


@pytest.fixture
def runner() -> AsyncRunner:
    return AsyncRunner(DummyRenderer())


@pytest.mark.asyncio
async def test_async_runner_passes_output(runner: AsyncRunner) -> None:
    async def step_fn(prev: int) -> int:
        return prev + 1

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
    )
    result = await runner.run_step(step, 41)
    assert result.status == "passed"
    assert result.output == 42


@pytest.mark.asyncio
async def test_async_runner_no_args(runner: AsyncRunner) -> None:
    async def step_fn() -> str:
        return "hello"

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
    )
    result = await runner.run_step(step, None)
    assert result.status == "passed"
    assert result.output == "hello"


@pytest.mark.asyncio
async def test_async_runner_timeout(runner: AsyncRunner) -> None:
    async def step_fn() -> str:
        await asyncio.sleep(0.5)
        return "too slow"

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
        timeout=0.1,
    )
    result = await runner.run_step(step, None)
    assert result.status == "failed"
    assert getattr(result.error, "__class__", None) is not None


@pytest.mark.asyncio
async def test_async_runner_exception(runner: AsyncRunner) -> None:
    async def step_fn() -> NoReturn:
        raise ValueError("boom")

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
    )
    result = await runner.run_step(step, None)
    assert result.status == "failed"
    assert isinstance(result.error, ValueError)


@pytest.mark.asyncio
async def test_async_runner_retry_success(runner: AsyncRunner) -> None:
    attempts = 0
    async def step_fn() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("fail")
        return "success"

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
        retries=3,
        retry_delay=0.01,
    )
    result = await runner.run_step(step, None)
    assert result.status == "passed"
    assert result.output == "success"
    assert result.retries_used == 2


@pytest.mark.asyncio
async def test_async_runner_retry_fail(runner: AsyncRunner) -> None:
    async def step_fn() -> NoReturn:
        raise ValueError("fail")

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
        retries=2,
        retry_delay=0.01,
    )
    result = await runner.run_step(step, None)
    assert result.status == "failed"
    assert result.retries_used == 2


@pytest.mark.asyncio
async def test_async_runner_skip_if(runner: AsyncRunner) -> None:
    async def step_fn() -> str:
        return "never run"

    step = StepDefinition(
        label="Test Step",
        fn=step_fn,
        skip_if=lambda: True,
    )
    result = await runner.run_step(step, None)
    assert result.status == "skipped"
