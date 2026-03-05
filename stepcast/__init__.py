"""stepcast — Every Python script deserves a voice.

Public API:
    from stepcast import Pipeline
"""

from __future__ import annotations

from stepcast.exceptions import PipelineAbortError, StepFailedError
from stepcast.models import RunReport, StepResult
from stepcast.pipeline import Pipeline

__version__ = "1.0.1"
__author__ = "Suneel Bose K"
__author_url__ = "https://github.com/bosekarmegam"

__all__ = [
    "Pipeline",
    "StepResult",
    "RunReport",
    "StepFailedError",
    "PipelineAbortError",
    "__version__",
]
