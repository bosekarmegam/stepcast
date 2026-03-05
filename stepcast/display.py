from __future__ import annotations

import sys
from typing import Any, cast

from stepcast.i18n import t
from stepcast.models import RunReport, StepResult
from stepcast.utils import fmt_time, terminal_supports_unicode, truncate_line


class Renderer:
    """Plain terminal renderer for pipeline output.

    Writes formatted step output to stdout. Uses Unicode symbols
    when the terminal supports them, ASCII fallback otherwise.

    All user-facing strings are sourced from the i18n layer.
    """

    def __init__(self, max_line_length: int = 200) -> None:
        self._unicode = terminal_supports_unicode()
        self._max_line = max_line_length

    def _sep(self) -> str:
        if self._unicode:
            return t("pipeline.separator")
        return t("pipeline.separator_ascii")

    def print_header(self, name: str) -> None:
        """Print the pipeline header block.

        Args:
            name: Pipeline name to display.
        """
        sep = self._sep()
        self._write(sep)
        self._write(f"  {t('pipeline.header', name=name)}")
        self._write(sep)
        self._write("")

    def print_step_start(self, label: str) -> None:
        """Print the step start line.

        Args:
            label: Step label.
        """
        if self._unicode:
            self._write(f"  {t('step.running', label=label)}")
        else:
            self._write(f"  {t('step.running_ascii', label=label)}")

    def print_stdout_line(self, line: str) -> None:
        """Print a single captured stdout line from a step.

        Args:
            line: Raw stdout line (will be truncated if too long).
        """
        prefix = (
            t("step.output_prefix")
            if self._unicode
            else t("step.output_prefix_ascii")
        )
        self._write(prefix + truncate_line(line, self._max_line))

    def print_step_done(self, result: StepResult) -> None:
        """Print the step completion line with status and duration.

        Args:
            result: Completed StepResult to render.
        """
        duration = fmt_time(result.duration)
        if result.status == "passed":
            key = "step.passed" if self._unicode else "step.passed_ascii"
            self._write(f"  {t(key, duration=duration)}")
        elif result.status == "skipped":
            key = "step.skipped" if self._unicode else "step.skipped_ascii"
            self._write(f"  {t(key)}")
        else:
            key = "step.failed" if self._unicode else "step.failed_ascii"
            self._write(f"  {t(key, duration=duration)}")
            if result.error:
                self._write(f"     {type(result.error).__name__}: {result.error}")
        if result.narration:
            self._write(f"     💬 {result.narration}")
        self._write("")

    def print_retry(self, attempt: int, total: int) -> None:
        """Print a retry attempt notification.

        Args:
            attempt: Current attempt number.
            total: Total allowed retries.
        """
        if self._unicode:
            self._write(f"  {t('step.retrying', attempt=attempt, total=total)}")
        else:
            self._write(f"  {t('step.retrying_ascii', attempt=attempt, total=total)}")

    def print_summary(self, report: RunReport) -> None:
        """Print the final pipeline summary block.

        Args:
            report: Completed RunReport to summarise.
        """
        sep = self._sep()
        self._write(sep)
        passed = len(report.passed_steps())
        failed = len(report.failed_steps())
        total = len(report.steps)
        duration = fmt_time(report.total_time)

        if report.success:
            key = "summary.passed" if self._unicode else "summary.passed_ascii"
            self._write(
                f"  {t(key, passed=passed, total=total, duration=duration)}"
            )
        else:
            key = "summary.failed" if self._unicode else "summary.failed_ascii"
            self._write(
                f"  {t(key, failed=failed, total=total, duration=duration)}"
            )
        self._write(sep)

    def print_dry_run_step(self, label: str) -> None:
        """Print a dry-run step line (no execution).

        Args:
            label: Step label.
        """
        if self._unicode:
            self._write(t("dryrun.step", label=label))
        else:
            self._write(t("dryrun.step_ascii", label=label))

    def print_dry_run_note(self) -> None:
        """Print the dry-run completion note."""
        self._write(t("dryrun.note"))

    def _write(self, text: str) -> None:
        """Write a line to stdout followed by a newline.

        Args:
            text: Text to output.
        """
        try:
            print(text, flush=True)
        except UnicodeEncodeError:
            # Last-resort encoding fallback
            encoded = text.encode(sys.stdout.encoding or "ascii", errors="replace")
            sys.stdout.buffer.write(encoded + b"\n")
            sys.stdout.buffer.flush()


def _try_rich_renderer() -> Any | None:  # noqa: ANN401
    """Attempt to load the Rich renderer if available.

    Returns:
        RichRenderer instance or None if rich not installed.
    """
    try:
        from stepcast.integrations.rich_display import (
            RichRenderer,
        )

        return RichRenderer()
    except ImportError:
        return None


def get_renderer(prefer_rich: bool | None = None) -> Renderer:
    """Get the best available renderer.

    Args:
        prefer_rich: None = auto-detect, True = require rich, False = plain.

    Returns:
        A Renderer instance (plain or rich).
    """
    if prefer_rich is False:
        return Renderer()
    rich_renderer = _try_rich_renderer()
    if rich_renderer is not None and prefer_rich in (True, None):
        return cast(Renderer, rich_renderer)
    return Renderer()
