from pydantic import BaseModel


class ConversationBaseRequest(BaseModel):
    user_id: str
