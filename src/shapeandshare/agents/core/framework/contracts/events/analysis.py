from typing import Literal

from .base import BaseEvent


class AnalysisEvent(BaseEvent):
    """Analysis-related events"""

    event_type: Literal["ANALYSIS_STARTED", "ANALYSIS_COMPLETED", "ANALYSIS_FAILED"]
    repository_id: str
    analysis_details: dict | None = None
    error_details: str | None = None
