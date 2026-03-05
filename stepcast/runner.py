from __future__ import annotations

import asyncio
import io
import sys
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from stepcast.display import Renderer
from stepcast.exceptions import StepFailedError
from stepcast.models import StepResult
from stepcast.step import StepDefinition
from stepcast.utils import scrub_stdout


@contextmanager
def _capture_stdout(
    renderer: Renderer, capture: bool
) -> Generator[io.StringIO, None, None]:
    """Context manager that captures stdout and live-streams it to the renderer.

    Writes live output directly to the original stdout (bypassing the
    replacement) so that ``renderer.print_stdout_line`` — which itself
    calls ``print()`` — does **not** recurse back into this writer.

    Args:
        renderer: Active Renderer for live output.
        capture: If False, stdout is not captured (passthrough).

    Yields:
        StringIO buffer containing captured output.
    """
    buffer = io.StringIO()
    if not capture:
        yield buffer
        return

    original_stdout = sys.stdout

    class _LiveWriter(io.TextIOBase):
        """Intercepts print() calls, mirrors to buffer + original stdout."""

        @property
        def encoding(self) -> str:  # type: ignore[override]
            return getattr(original_stdout, "encoding", "utf-8")

        def write(self, s: str) -> int:
            if not s:
                return 0
            # Store in buffer for StepResult.stdout
            buffer.write(s)
            # Stream live to the real terminal — write directly to
            # original_stdout so we never re-enter _LiveWriter.
            for line in s.splitlines(keepends=True):
                stripped = line.rstrip("\n\r")
                if stripped:
                    # Temporarily restore stdout so renderer.print_stdout_line
                    # writes to the real terminal, not back here.
                    sys.stdout = original_stdout
                    try:
                        renderer.print_stdout_line(stripped)
                    finally:
                        sys.stdout = self
            return len(s)

        def flush(self) -> None:
            try:
                if original_stdout is not None and hasattr(original_stdout, "flush"):
                    original_stdout.flush()
            except Exception:
                pass

        def isatty(self) -> bool:
            return False

    sys.stdout = _LiveWriter()
    try:
        yield buffer
    finally:
        sys.stdout = original_stdout


class Runner:
    """Synchronous step execution engine.

    Handles retries, timeouts, skip logic, output capture,
    and StepResult production for each step.
    """

    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    def run_step(
        self,
        step: StepDefinition,
        prev_output: Any,  # noqa: ANN401
    ) -> StepResult:
        """Execute a single step and return its result.

        Args:
            step: The step definition to execute.
            prev_output: Output from the previous step (passed as first arg).

        Returns:
            A completed StepResult.
        """
        timestamp = datetime.utcnow()

        # Evaluate skip condition
        if step.skip_if is not None:
            try:
                should_skip = step.skip_if()
            except Exception:
                should_skip = False
            if should_skip:
                self._renderer.print_step_start(step.label)
                result = StepResult(
                    label=step.label,
                    status="skipped",
                    duration=0.0,
                    timestamp=timestamp,
                    tags=step.tags,
                )
                self._renderer.print_step_done(result)
                return result

        self._renderer.print_step_start(step.label)

        last_error: BaseException | None = None
        captured_stdout = ""
        output: Any = None
        attempts = step.retries + 1

        for attempt in range(1, attempts + 1):
            if attempt > 1:
                self._renderer.print_retry(attempt - 1, step.retries)
                delay = step.retry_delay * (2 ** (attempt - 2))
                time.sleep(delay)

            start = time.perf_counter()
            try:
                with _capture_stdout(self._renderer, step.capture_output) as buf:
                    if step.timeout is not None:
                        output = self._run_with_timeout(
                            step, prev_output, step.timeout
                        )
                    else:
                        output = self._invoke(step, prev_output)
                captured_stdout = scrub_stdout(buf.getvalue())
                duration = time.perf_counter() - start

                result = StepResult(
                    label=step.label,
                    status="passed",
                    duration=duration,
                    output=output,
                    stdout=captured_stdout,
                    retries_used=attempt - 1,
                    tags=step.tags,
                    timestamp=timestamp,
                )
                self._renderer.print_step_done(result)
                return result

            except Exception as exc:
                duration = time.perf_counter() - start
                last_error = exc
                if attempt == attempts:
                    result = StepResult(
                        label=step.label,
                        status="failed",
                        duration=duration,
                        stdout=scrub_stdout(
                            "" if not step.capture_output else ""
                        ),
                        error=exc,
                        retries_used=attempt - 1,
                        tags=step.tags,
                        timestamp=timestamp,
                    )
                    self._renderer.print_step_done(result)
                    return result

        # Should never reach here
        return StepResult(
            label=step.label,
            status="failed",
            duration=0.0,
            error=last_error,
            tags=step.tags,
            timestamp=timestamp,
        )

    def _invoke(self, step: StepDefinition, prev_output: Any) -> Any:  # noqa: ANN401
        """Call the step function, passing prev_output only if the function accepts it.

        Args:
            step: Step to invoke.
            prev_output: Output from the previous step.

        Returns:
            Return value of the step function.
        """
        import inspect

        sig = inspect.signature(step.fn)
        if sig.parameters:
            return step.fn(prev_output)
        return step.fn()

    def _run_with_timeout(
        self, step: StepDefinition, prev_output: Any, timeout: float  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Run a step function with a strict timeout.

        Args:
            step: Step to execute.
            prev_output: Output from the previous step.
            timeout: Maximum allowed seconds.

        Returns:
            Return value of the step function.

        Raises:
            StepFailedError: If the timeout expires.
            Exception: Any exception from the step function.
        """
        result_holder: list[Any] = [None]
        exc_holder: list[BaseException | None] = [None]

        def target() -> None:
            try:
                result_holder[0] = self._invoke(step, prev_output)
            except Exception as e:
                exc_holder[0] = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            raise StepFailedError(
                step.label,
                TimeoutError(f"Step timed out after {timeout}s"),
            )

        if exc_holder[0] is not None:
            raise exc_holder[0]

        return result_holder[0]


class AsyncRunner:
    """Asynchronous step execution engine for async def steps."""

    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer

    async def run_step(
        self,
        step: StepDefinition,
        prev_output: Any,  # noqa: ANN401
    ) -> StepResult:
        """Execute a single async step and return its result.

        Args:
            step: The step definition (must be async).
            prev_output: Output from the previous step.

        Returns:
            A completed StepResult.
        """
        import inspect

        timestamp = datetime.utcnow()

        if step.skip_if is not None:
            try:
                should_skip = step.skip_if()
            except Exception:
                should_skip = False
            if should_skip:
                self._renderer.print_step_start(step.label)
                result = StepResult(
                    label=step.label,
                    status="skipped",
                    duration=0.0,
                    timestamp=timestamp,
                    tags=step.tags,
                )
                self._renderer.print_step_done(result)
                return result

        self._renderer.print_step_start(step.label)

        last_error: BaseException | None = None
        attempts = step.retries + 1

        for attempt in range(1, attempts + 1):
            if attempt > 1:
                self._renderer.print_retry(attempt - 1, step.retries)
                delay = step.retry_delay * (2 ** (attempt - 2))
                await asyncio.sleep(delay)

            start = time.perf_counter()
            try:
                sig = inspect.signature(step.fn)
                if step.timeout is not None:
                    coro = step.fn(prev_output) if sig.parameters else step.fn()
                    output = await asyncio.wait_for(coro, timeout=step.timeout)
                else:
                    output = (
                        await step.fn(prev_output)
                        if sig.parameters
                        else await step.fn()
                    )
                duration = time.perf_counter() - start
                result = StepResult(
                    label=step.label,
                    status="passed",
                    duration=duration,
                    output=output,
                    retries_used=attempt - 1,
                    tags=step.tags,
                    timestamp=timestamp,
                )
                self._renderer.print_step_done(result)
                return result

            except asyncio.TimeoutError as exc:
                duration = time.perf_counter() - start
                last_error = exc
                result = StepResult(
                    label=step.label,
                    status="failed",
                    duration=duration,
                    error=exc,
                    retries_used=attempt - 1,
                    tags=step.tags,
                    timestamp=timestamp,
                )
                self._renderer.print_step_done(result)
                return result

            except Exception as exc:
                duration = time.perf_counter() - start
                last_error = exc
                if attempt == attempts:
                    result = StepResult(
                        label=step.label,
                        status="failed",
                        duration=duration,
                        error=exc,
                        retries_used=attempt - 1,
                        tags=step.tags,
                        timestamp=timestamp,
                    )
                    self._renderer.print_step_done(result)
                    return result

        return StepResult(
            label=step.label,
            status="failed",
            duration=0.0,
            error=last_error,
            tags=step.tags,
            timestamp=timestamp,
        )
