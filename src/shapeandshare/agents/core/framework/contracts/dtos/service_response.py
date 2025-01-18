from pydantic import BaseModel


class ServiceResponse(BaseModel):
    """Standard service response"""

    success: bool
    data: dict | None = None
    error: str | None = None
