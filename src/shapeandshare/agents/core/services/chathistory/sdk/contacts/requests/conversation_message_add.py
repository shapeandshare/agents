from .conversation_base import ConversationBaseRequest


class ConversationMessageAddRequest(ConversationBaseRequest):
    content: str
    role: str
