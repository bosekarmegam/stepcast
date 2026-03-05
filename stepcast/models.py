from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from stepcast.utils import fmt_time


@dataclass
class StepResult:
    """Result of a single executed pipeline step.

    Attributes:
        label: Human-readable step name.
        status: Execution outcome — 'passed', 'failed', or 'skipped'.
        duration: Elapsed time in seconds.
        output: Return value from the step function.
        stdout: Captured print output from the step.
        error: Exception instance if the step failed, else None.
        narration: Gemini AI narration text, or None.
        retries_used: Number of retry attempts consumed.
        tags: Metadata tags attached to this step.
        timestamp: When this step started executing.
    """

    label: str
    status: str  # "passed" | "failed" | "skipped"
    duration: float
    output: Any = None
    stdout: str = ""
    error: BaseException | None = None
    narration: str | None = None
    retries_used: int = 0
    tags: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_json(self) -> dict[str, Any]:
        """Serialise this result to a JSON-compatible dictionary.

        Returns:
            Dict safe for json.dumps().
        """
        return {
            "label": self.label,
            "status": self.status,
            "duration": self.duration,
            "stdout": self.stdout,
            "error": str(self.error) if self.error else None,
            "narration": self.narration,
            "retries_used": self.retries_used,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "output_repr": repr(self.output)[:500],
        }


@dataclass
class RunReport:
    """Complete report of a finished pipeline run.

    Attributes:
        pipeline_name: Name of the pipeline.
        success: True if all steps passed.
        total_time: Total elapsed time in seconds.
        steps: Ordered list of StepResult objects.
        timestamp: When the run started.
    """

    pipeline_name: str
    success: bool
    total_time: float
    steps: list[StepResult]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_json(self) -> dict[str, Any]:
        """Serialise this report to a JSON-compatible dictionary.

        Returns:
            Dict safe for json.dumps().
        """
        return {
            "pipeline_name": self.pipeline_name,
            "success": self.success,
            "total_time": self.total_time,
            "timestamp": self.timestamp.isoformat(),
            "steps": [s.to_json() for s in self.steps],
        }

    def to_file(self, path: str) -> None:
        """Save this report as a JSON file.

        Args:
            path: File path to write to (created if not exists).
        """
        from pathlib import Path

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, indent=2)

    def summary(self) -> str:
        """One-line human-readable summary of the run.

        Returns:
            Summary string with counts and total time.

        Example:
            >>> report.summary()
            '3 of 3 steps passed in 0.01s'
        """
        passed = len(self.passed_steps())
        total = len(self.steps)
        duration = fmt_time(self.total_time)
        if self.success:
            return f"{passed} of {total} steps passed in {duration}"
        failed = len(self.failed_steps())
        return f"{failed} of {total} steps failed in {duration}"

    def failed_steps(self) -> list[StepResult]:
        """Return only the steps that failed.

        Returns:
            List of failed StepResult objects.
        """
        return [s for s in self.steps if s.status == "failed"]

    def passed_steps(self) -> list[StepResult]:
        """Return only the steps that passed.

        Returns:
            List of passed StepResult objects.
        """
        return [s for s in self.steps if s.status == "passed"]

    def skipped_steps(self) -> list[StepResult]:
        """Return only the steps that were skipped.

        Returns:
            List of skipped StepResult objects.
        """
        return [s for s in self.steps if s.status == "skipped"]
