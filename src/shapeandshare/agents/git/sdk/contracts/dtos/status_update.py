from pydantic import BaseModel

from ..types.processing_status import ProcessingStatus


class RepositoryStatusUpdateRequest(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    repository_id: str
    status: ProcessingStatus
