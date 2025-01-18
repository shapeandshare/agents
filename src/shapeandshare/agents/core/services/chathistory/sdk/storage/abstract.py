from abc import abstractmethod

from pydantic import BaseModel

from ..contacts.models.conversation import Conversation
from ..contacts.models.conversation_summary import ConversationSummary


class ChatStorageInterface(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    """Abstract interface for chat storage implementations"""

    @abstractmethod
    async def conversation_save(self, conversation: Conversation, user_id: str) -> str:
        """Save or update a conversation"""

    @abstractmethod
    async def conversation_get(self, conversation_id: str, user_id: str) -> Conversation:
        """Retrieve a conversation by ID"""

    @abstractmethod
    async def conversation_delete(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""

    @abstractmethod
    async def conversations_list(self, user_id: str, limit: int = 10, offset: int = 0) -> list[ConversationSummary]:
        """List conversations for a user"""
