from datetime import datetime

from pydantic import BaseModel, Field

from .message import Message


class Conversation(BaseModel):
    """Complete chat conversation"""

    id: str
    user_id: str
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)
