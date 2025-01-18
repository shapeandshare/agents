from datetime import datetime

from pydantic import BaseModel


class BaseCommand(BaseModel):
    """Base command class"""

    command_id: str
    timestamp: datetime
    correlation_id: str
