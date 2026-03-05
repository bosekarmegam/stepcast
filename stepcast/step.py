from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepDefinition:
    """Internal record of a registered pipeline step.

    Attributes:
        fn: The wrapped user function.
        label: Human-readable name for display.
        retries: Number of retry attempts on failure.
        retry_delay: Base delay in seconds between retries (exponential backoff).
        skip_if: Callable returning bool — skip step if True.
        timeout: Max seconds for the step; raises StepFailedError if exceeded.
        tags: Metadata tags for filtering.
        capture_output: Whether to capture and stream stdout.
    """

    fn: Callable[..., Any]
    label: str
    retries: int = 0
    retry_delay: float = 1.0
    skip_if: Callable[[], bool] | None = None
    timeout: float | None = None
    tags: list[str] = field(default_factory=list)
    capture_output: bool = True

    @property
    def is_async(self) -> bool:
        """Whether the wrapped function is a coroutine function."""
        return inspect.iscoroutinefunction(self.fn)
