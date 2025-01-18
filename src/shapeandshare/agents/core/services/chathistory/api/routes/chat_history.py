from fastapi import APIRouter, Depends

from ...sdk.contacts.models.conversation import Conversation
from ...sdk.contacts.models.conversation_summary import ConversationSummary
from ...sdk.contacts.requests.conversation_create import ConversationCreateRequest
from ...sdk.contacts.requests.conversation_delete import ConversationDeleteRequest
from ...sdk.contacts.requests.conversation_get import ConversationGetRequest
from ...sdk.contacts.requests.conversation_message_add import ConversationMessageAddRequest
from ...sdk.contacts.requests.conversations_get import ConversationsGetRequest
from ...service import ChatHistoryService
from ..context import context
from ..middleware.error import error_handler

router = APIRouter(prefix="/chat-history", tags=["chat-history"])


async def get_service() -> ChatHistoryService:
    # In practice, you'd get this from your dependency injection container
    return context["chathistory_service"]


@router.post("/conversations")
@error_handler
async def conversation_create(
    request: ConversationCreateRequest, service: ChatHistoryService = Depends(get_service)
) -> Conversation:
    return await service.conversation_create(user_id=request.user_id)


@router.post("/conversations/{conversation_id}/messages")
@error_handler
async def message_add(
    request: ConversationMessageAddRequest, conversation_id: str, service: ChatHistoryService = Depends(get_service)
) -> Conversation:
    return await service.message_add(
        conversation_id=conversation_id, user_id=request.user_id, content=request.content, role=request.role
    )


@router.get("/conversations/{conversation_id}")
@error_handler
async def conversation_get(
    request: ConversationGetRequest, conversation_id: str, service: ChatHistoryService = Depends(get_service)
) -> Conversation:
    return await service.conversation_get(conversation_id=conversation_id, user_id=request.user_id)


@router.get("/users/{user_id}/conversations")
@error_handler
async def conversations_list(
    request: ConversationsGetRequest, user_id: str, service: ChatHistoryService = Depends(get_service)
) -> list[ConversationSummary]:
    return await service.user_conversations_list(user_id=user_id, limit=request.limit, offset=request.offset)


@router.delete("/conversations/{conversation_id}")
@error_handler
async def conversation_delete(
    request: ConversationDeleteRequest, conversation_id: str, service: ChatHistoryService = Depends(get_service)
) -> bool:
    return await service.conversation_delete(conversation_id=conversation_id, user_id=request.user_id)
