from pydantic import BaseModel


class LLMHyperParameters(BaseModel):
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    timeout: int | None = None
    max_retries: int | None = None
