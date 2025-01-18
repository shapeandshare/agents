import logging
import uuid

from fastapi import HTTPException
from pydantic import BaseModel

from .sdk.contacts.models.conversation import Conversation
from .sdk.contacts.models.conversation_summary import ConversationSummary
from .sdk.contacts.models.message import Message
from .sdk.storage.mongodb import MongoDBStorage

logger = logging.getLogger(__name__)


class ChatHistoryService(BaseModel):
    storage: MongoDBStorage

    async def conversation_create(self, user_id: str) -> Conversation:
        # create a new conversation
        conversation = Conversation(id=str(uuid.uuid4()), user_id=user_id, messages=[])
        await self.storage.conversation_save(conversation=conversation, user_id=user_id)
        return conversation

    async def message_add(
        self, conversation_id: str, user_id: str, content: str, role: str, metadata: dict = None
    ) -> Conversation:
        """Add a new message to a conversation"""
        try:
            conversation: Conversation | None = await self.storage.conversation_get(
                conversation_id=conversation_id, user_id=user_id
            )
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            message = Message(content=content, role=role, metadata=metadata or {})
            conversation.messages.append(message)
            conversation.updated_at = message.timestamp

            await self.storage.conversation_save(conversation=conversation, user_id=user_id)
            return conversation

        except Exception as error:
            msg: str = f"Error adding message to conversation {conversation_id}: {str(error)}"
            logger.error(msg)
            raise HTTPException(status_code=500, detail="Error adding message") from error

    async def conversation_get(self, conversation_id: str, user_id: str) -> Conversation:
        """Retrieve conversation history"""
        try:
            conversation: Conversation | None = await self.storage.conversation_get(
                conversation_id=conversation_id, user_id=user_id
            )

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            return conversation
        except HTTPException:
            raise
        except Exception as error:
            msg: str = f"Error retrieving conversation {conversation_id}: {str(error)}"
            logger.error(msg)
            raise HTTPException(status_code=500, detail="Error retrieving conversation")

    async def user_conversations_list(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> list[ConversationSummary]:
        """List conversations for a user"""
        try:
            return await self.storage.conversations_list(user_id=user_id, limit=limit, offset=offset)
        except Exception as error:
            msg: str = f"Error listing conversations for user {user_id}: {str(error)}"
            logger.error(msg)
            raise HTTPException(status_code=500, detail="Error listing conversations")

    async def conversation_delete(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        try:
            return await self.storage.conversation_delete(conversation_id=conversation_id, user_id=user_id)
        except Exception as error:
            msg: str = f"Error deleting conversation {conversation_id}: {str(error)}"
            logger.error(msg)
            raise HTTPException(status_code=500, detail="Error deleting conversation")
