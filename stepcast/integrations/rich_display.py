from __future__ import annotations

from typing import Any

from stepcast.display import Renderer
from stepcast.models import RunReport, StepResult
from stepcast.utils import fmt_time


class RichRenderer(Renderer):
    """Rich-powered terminal renderer with spinners, colour, and progress.

    Falls back to the plain Renderer if rich is not installed.
    Lazy imports rich so the core library never crashes without it.
    """

    def __init__(self, max_line_length: int = 200) -> None:
        super().__init__(max_line_length)
        self._console: Any = self._load_console()

    def _load_console(self) -> Any:  # noqa: ANN401
        """Load a Rich Console instance.

        Returns:
            rich.console.Console or None if not available.
        """
        try:
            from rich.console import Console

            return Console(highlight=False)
        except ImportError:
            return None

    def _write(self, text: str) -> None:
        if self._console is not None:
            self._console.print(text)
        else:
            super()._write(text)

    def print_step_start(self, label: str) -> None:
        if self._console:
            self._console.print(f"  [bold cyan]▶[/bold cyan]  {label}...")
        else:
            super().print_step_start(label)

    def print_step_done(self, result: StepResult) -> None:
        if not self._console:
            super().print_step_done(result)
            return

        duration = fmt_time(result.duration)
        if result.status == "passed":
            self._console.print(
                f"  [bold green]✅[/bold green]  Done  [dim]({duration})[/dim]"
            )
        elif result.status == "skipped":
            self._console.print(
                "  [bold yellow]⏭[/bold yellow]  Skipped  [dim](skip_if returned True)[/dim]"  # noqa: E501
            )
        else:
            self._console.print(
                f"  [bold red]❌[/bold red]  Failed  [dim]({duration})[/dim]"
            )
            if result.error:
                self._console.print(
                    f"     [red]{type(result.error).__name__}: {result.error}[/red]"
                )
        if result.narration:
            self._console.print(f"     [blue]💬 {result.narration}[/blue]")
        self._console.print("")

    def print_retry(self, attempt: int, total: int) -> None:
        if self._console:
            self._console.print(
                f"  [yellow]🔄  Retrying ({attempt}/{total})...[/yellow]"
            )
        else:
            super().print_retry(attempt, total)

    def print_header(self, name: str) -> None:
        if self._console:

            self._console.rule(f"[bold]📡  {name}[/bold]", style="dim")
            self._console.print("")
        else:
            super().print_header(name)

    def print_summary(self, report: RunReport) -> None:
        if not self._console:
            super().print_summary(report)
            return


        duration = fmt_time(report.total_time)
        passed = len(report.passed_steps())
        total = len(report.steps)
        failed = len(report.failed_steps())

        if report.success:
            self._console.rule(
                f"[bold green]✅  {passed} of {total} steps passed   Total: {duration}[/bold green]",  # noqa: E501
                style="green dim",
            )
        else:
            self._console.rule(
                f"[bold red]❌  {failed} of {total} steps failed   Total: {duration}[/bold red]",  # noqa: E501
                style="red dim",
            )
