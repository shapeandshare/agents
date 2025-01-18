from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel


class ChatHistory(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    conversation_id: str | None = None
    history: list[HumanMessage | AIMessage]
