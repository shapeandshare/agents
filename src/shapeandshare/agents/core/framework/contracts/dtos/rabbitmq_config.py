from pydantic import BaseModel


class RabbitMQConfig(BaseModel):
    hostname: str
    port: int
    username: str
    password: str
