import os
from typing import Any
from urllib.parse import quote_plus

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..contacts.models.conversation import Conversation
from ..contacts.models.conversation_summary import ConversationSummary
from .abstract import ChatStorageInterface


def get_mongodb_uri() -> tuple[str, str]:
    username: str = os.environ["MONGODB_USERNAME"]
    password: str = os.environ["MONGODB_PASSWORD"]
    hostname: str = os.environ["MONGODB_HOSTNAME"]
    port: int = int(os.environ["MONGODB_PORT"])
    database: str = os.environ["MONGODB_DATABASE"]

    uri: str = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{hostname}:{port}"
    return uri, database


class MongoDBStorage(ChatStorageInterface):
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None
    conversations: Any | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        uri, database = get_mongodb_uri()
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database]
        self.conversations = self.db.conversations

    async def conversation_save(self, conversation: Conversation, user_id: str) -> str:
        await self.conversations.update_one(
            {"id": conversation.id, "user_id": user_id}, {"$set": conversation.model_dump()}, upsert=True
        )
        return conversation.id

    async def conversation_get(self, conversation_id: str, user_id: str) -> Conversation | None:
        doc: dict | None = await self.conversations.find_one({"id": conversation_id, "user_id": user_id})
        return Conversation.model_validate(doc) if doc else None

    async def conversation_delete(self, conversation_id: str, user_id: str) -> bool:
        result = await self.conversations.delete_one({"id": conversation_id, "user_id": user_id})
        return result.deleted_count > 0

    async def conversations_list(self, user_id: str, limit: int = 10, offset: int = 0) -> list[ConversationSummary]:
        cursor = self.conversations.find({"user_id": user_id}, sort=[("updated_at", -1)], skip=offset, limit=limit)
        conversations = []
        async for doc in cursor:
            conv = Conversation.model_validate(doc)
            summary = ConversationSummary(
                id=conv.id,
                user_id=conv.user_id,
                message_count=len(conv.messages),
                last_message_at=conv.messages[-1].timestamp if conv.messages else None,
            )
            conversations.append(summary)
        return conversations
