from pydantic import BaseModel


class BaseChatRequest(BaseModel):
    id: str
    url: str


class ChatRequest(BaseChatRequest):
    prompt: str
    k: int  # the number of documents to return from vector search when submitting as context
    conversation_id: str | None = None
