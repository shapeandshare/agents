from datetime import datetime

from pydantic import BaseModel


class BaseEvent(BaseModel):
    """Base event class with common fields"""

    event_id: str
    event_type: str
    timestamp: datetime
    correlation_id: str
    source_service: str
