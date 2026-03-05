from __future__ import annotations

import asyncio
import contextlib
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from stepcast.display import Renderer, get_renderer
from stepcast.exceptions import PipelineAbortError, StepFailedError
from stepcast.models import RunReport, StepResult
from stepcast.runner import AsyncRunner, Runner
from stepcast.step import StepDefinition


class Pipeline:
    """Orchestrates a sequence of named, observable steps.

    Each step is registered via the ``@pipe.step()`` decorator.
    Calling ``pipe.run()`` executes all steps in order, streaming
    live output to the terminal and returning a ``RunReport``.

    Args:
        name: Human-readable pipeline name shown in the header.
        fail_fast: Abort on first step failure (default True).
        narrate: Enable Gemini AI step narration (requires API key).
        rich: None = auto-detect rich library, True = require, False = plain.
        log_file: Path to save run JSON report, or None.
        show_summary: Print final summary line (default True).
        timezone: Timezone label for timestamps (default 'UTC').
        dashboard: Stream run to local dashboard. True = localhost:4321,
            or a URL string for a team server.

    Example:
        >>> pipe = Pipeline("My Pipeline")
        >>> @pipe.step("Load data")
        ... def load():
        ...     return [1, 2, 3]
        >>> report = pipe.run()
        >>> report.success
        True
    """

    def __init__(
        self,
        name: str,
        fail_fast: bool = True,
        narrate: bool = False,
        rich: bool | None = None,
        log_file: str | Path | None = None,
        show_summary: bool = True,
        timezone: str = "UTC",
        dashboard: bool | str = False,
    ) -> None:
        self.name = name
        self.fail_fast = fail_fast
        self.narrate = narrate
        self.rich = rich
        self.log_file = Path(log_file) if log_file else None
        self.show_summary = show_summary
        self.timezone = timezone
        self.dashboard = dashboard

        self._steps: list[StepDefinition] = []
        self._renderer: Renderer = get_renderer(rich)
        self.last_run: RunReport | None = None

    def step(
        self,
        label: str,
        retries: int = 0,
        retry_delay: float = 1.0,
        skip_if: Callable[[], bool] | None = None,
        timeout: float | None = None,
        tags: list[str] | None = None,
        capture_output: bool = True,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Register a function as a pipeline step (decorator factory).

        Args:
            label: Human-readable step name displayed in output.
            retries: Number of retry attempts on failure.
            retry_delay: Base delay in seconds between retries.
            skip_if: Callable returning bool — step is skipped if True.
            timeout: Max seconds; raises StepFailedError if exceeded.
            tags: Metadata tags for step filtering.
            capture_output: Stream stdout live (default True).

        Returns:
            Decorator that wraps the function and registers the step.

        Example:
            >>> @pipe.step("Fetch data", retries=3, timeout=30)
            ... def fetch():
            ...     return requests.get("https://api.example.com/data").json()
        """

        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            step_def = StepDefinition(
                fn=fn,
                label=label,
                retries=retries,
                retry_delay=retry_delay,
                skip_if=skip_if,
                timeout=timeout,
                tags=tags or [],
                capture_output=capture_output,
            )
            self._steps.append(step_def)
            return fn

        return decorator

    def run(
        self,
        initial: Any = None,  # noqa: ANN401
        steps: list[str] | None = None,
        dry_run: bool = False,
    ) -> RunReport:
        """Execute all registered steps in order.

        Args:
            initial: Value passed as input to the first step.
            steps: If given, only run steps whose label or tags match.
            dry_run: Print step labels without executing them.

        Returns:
            A RunReport containing results for all steps.

        Raises:
            PipelineAbortError: If fail_fast is True and a step fails.

        Example:
            >>> report = pipe.run(initial={"key": "value"}, dry_run=False)
            >>> report.success
            True
        """
        # Filter steps if requested
        active_steps = self._filter_steps(steps)

        if dry_run:
            return self._dry_run(active_steps)

        # Check for any async steps and route accordingly
        if any(s.is_async for s in active_steps):
            return asyncio.run(self._run_async(active_steps, initial))

        return self._run_sync(active_steps, initial)

    def _filter_steps(
        self, filter_names: list[str] | None
    ) -> list[StepDefinition]:
        """Filter steps by label or tag.

        Args:
            filter_names: List of labels or tags to include.

        Returns:
            Filtered list of step definitions.
        """
        if filter_names is None:
            return list(self._steps)
        result = []
        for s in self._steps:
            if s.label in filter_names or any(t in s.tags for t in filter_names):
                result.append(s)
        return result

    def _dry_run(self, active_steps: list[StepDefinition]) -> RunReport:
        """Execute a dry run — print steps without invoking them.

        Args:
            active_steps: Steps to display.

        Returns:
            RunReport with all steps marked as skipped.
        """
        self._renderer.print_header(self.name)
        results = []
        for s in active_steps:
            self._renderer.print_dry_run_step(s.label)
            results.append(
                StepResult(
                    label=s.label,
                    status="skipped",
                    duration=0.0,
                    tags=s.tags,
                )
            )
        self._renderer.print_dry_run_note()
        report = RunReport(
            pipeline_name=self.name,
            success=True,
            total_time=0.0,
            steps=results,
            timestamp=datetime.utcnow(),
        )
        self.last_run = report
        return report

    def _run_sync(
        self, active_steps: list[StepDefinition], initial: Any  # noqa: ANN401
    ) -> RunReport:
        """Execute all steps synchronously.

        Args:
            active_steps: Steps to execute.
            initial: Initial value for the first step.

        Returns:
            Completed RunReport.

        Raises:
            PipelineAbortError: If fail_fast=True and a step fails.
        """
        self._renderer.print_header(self.name)
        runner = Runner(self._renderer)
        results: list[StepResult] = []
        prev_output: Any = initial
        start_time = time.perf_counter()

        for step_def in active_steps:
            result = runner.run_step(step_def, prev_output)
            results.append(result)

            # Optional Gemini narration (non-blocking)
            if self.narrate and result.status == "passed":
                self._add_narration(result)

            if result.status == "passed":
                prev_output = result.output
            elif result.status == "failed" and self.fail_fast:
                total_time = time.perf_counter() - start_time
                report = RunReport(
                    pipeline_name=self.name,
                    success=False,
                    total_time=total_time,
                    steps=results,
                    timestamp=datetime.utcnow(),
                )
                if self.show_summary:
                    self._renderer.print_summary(report)
                self._save_report(report)
                self.last_run = report
                raise PipelineAbortError(
                    self.name,
                    result.label,
                    StepFailedError(result.label, result.error),
                )

        total_time = time.perf_counter() - start_time
        success = all(r.status != "failed" for r in results)
        report = RunReport(
            pipeline_name=self.name,
            success=success,
            total_time=total_time,
            steps=results,
            timestamp=datetime.utcnow(),
        )
        if self.show_summary:
            self._renderer.print_summary(report)
        self._save_report(report)
        self.last_run = report
        return report

    async def _run_async(
        self, active_steps: list[StepDefinition], initial: Any  # noqa: ANN401
    ) -> RunReport:
        """Execute steps asynchronously (mixed sync/async supported).

        Args:
            active_steps: Steps to execute.
            initial: Initial value for the first step.

        Returns:
            Completed RunReport.
        """

        self._renderer.print_header(self.name)
        async_runner = AsyncRunner(self._renderer)
        sync_runner = Runner(self._renderer)
        results: list[StepResult] = []
        prev_output: Any = initial
        start_time = time.perf_counter()

        for step_def in active_steps:
            if step_def.is_async:
                result = await async_runner.run_step(step_def, prev_output)
            else:
                result = sync_runner.run_step(step_def, prev_output)
            results.append(result)

            if result.status == "passed":
                prev_output = result.output
            elif result.status == "failed" and self.fail_fast:
                break

        total_time = time.perf_counter() - start_time
        success = all(r.status != "failed" for r in results)
        report = RunReport(
            pipeline_name=self.name,
            success=success,
            total_time=total_time,
            steps=results,
            timestamp=datetime.utcnow(),
        )
        if self.show_summary:
            self._renderer.print_summary(report)
        self._save_report(report)
        self.last_run = report
        return report

    def _add_narration(self, result: StepResult) -> None:
        """Add Gemini narration to a step result (non-blocking).

        Args:
            result: A passed StepResult to narrate.
        """
        try:
            from stepcast.integrations.gemini import narrate_step

            narration = narrate_step(
                label=result.label,
                stdout=result.stdout,
                duration=result.duration,
                output_summary=repr(result.output)[:200],
            )
            result.narration = narration
        except Exception:
            pass  # Narration must never disrupt the pipeline

    def _save_report(self, report: RunReport) -> None:
        """Save the run report to a file if log_file is configured.

        Args:
            report: Completed RunReport to save.
        """
        if self.log_file:
            with contextlib.suppress(Exception):
                report.to_file(str(self.log_file))
