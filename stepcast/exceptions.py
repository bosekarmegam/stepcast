from __future__ import annotations


class StepFailedError(Exception):
    """Raised when a step fails after exhausting all retries.

    Args:
        label: The human-readable step label.
        cause: The original exception that caused the failure.
    """

    def __init__(self, label: str, cause: BaseException | None = None) -> None:
        self.label = label
        self.cause = cause
        msg = f"Step '{label}' failed"
        if cause is not None:
            msg += f": {cause}"
        super().__init__(msg)


class PipelineAbortError(Exception):
    """Raised by Pipeline.run() when fail_fast=True and a step fails.

    Args:
        pipeline_name: Name of the pipeline that aborted.
        failed_label: Label of the step that caused the abort.
        cause: The StepFailedError that triggered the abort.
    """

    def __init__(
        self,
        pipeline_name: str,
        failed_label: str,
        cause: StepFailedError | None = None,
    ) -> None:
        self.pipeline_name = pipeline_name
        self.failed_label = failed_label
        self.cause = cause
        super().__init__(
            f"Pipeline '{pipeline_name}' aborted at step '{failed_label}'"
        )
