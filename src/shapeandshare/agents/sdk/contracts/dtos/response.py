from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Response[T](BaseModel):
    data: T
