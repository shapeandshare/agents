from typing import Literal

from .base import BaseEvent


class RepositoryEvent(BaseEvent):
    """Repository-related events"""

    event_type: Literal[
        "REPOSITORY_PROCESS",
        "REPOSITORY_CLONED",
        "REPOSITORY_DELETED",
        "REPOSITORY_CLONE_FAILED",
        "REPOSITORY_ANALYZED",
        "REPOSITORY_ANALYSIS_FAILED",
        "REPOSITORY_DELETE_FAILED",
    ]
    repository_id: str
    collection_id: str | None = None
    url: str | None = None
    error_details: str | None = None
