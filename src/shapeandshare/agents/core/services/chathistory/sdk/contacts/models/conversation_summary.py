from datetime import datetime

from pydantic import BaseModel


class ConversationSummary(BaseModel):
    """Summary view of a conversation"""

    id: str
    user_id: str
    message_count: int
    last_message_at: datetime | None = None
