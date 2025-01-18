from .....core.framework.contracts.models.metadata import Metadata
from ..types.processing_status import ProcessingStatus


class GitMetadata(Metadata):
    status: ProcessingStatus | None = None
