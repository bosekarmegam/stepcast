import asyncio
from typing import Any, NoReturn

from stepcast.pipeline import Pipeline


def test_pipeline_run_async() -> None:
    pipe = Pipeline("Async Test")

    @pipe.step("Sync Step")
    def sync_step() -> int:
        return 1

    @pipe.step("Async Step")
    async def async_step(prev: int) -> int:
        await asyncio.sleep(0.01)
        return prev + 1

    report = pipe.run()
    assert report.success
    assert len(report.steps) == 2
    assert report.steps[1].output == 2


def test_pipeline_run_async_fail_fast() -> None:
    pipe = Pipeline("Async Test FailFast", fail_fast=True)

    @pipe.step("Async Step 1")
    async def async_step1() -> NoReturn:
        raise ValueError("boom")

    @pipe.step("Async Step 2")
    async def async_step2(prev: Any) -> int:  # noqa: ANN401
        return 2

    report = pipe.run()
    assert not report.success
    assert len(report.steps) == 1
    assert report.steps[0].status == "failed"
