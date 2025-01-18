from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Individual chat message"""

    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
