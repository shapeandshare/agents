from pydantic import BaseModel


class Metadata(BaseModel):
    id: str | None = None
    col_id: str
    conversation_id: str
