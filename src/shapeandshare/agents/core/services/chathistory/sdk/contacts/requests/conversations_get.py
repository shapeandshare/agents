from pydantic import BaseModel


class ConversationsGetRequest(BaseModel):
    limit: int = 10
    offset: int = 0
