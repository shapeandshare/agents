""" Request Status Codes Definition """

from pydantic import BaseModel


class RequestStatusCodes(BaseModel):
    """
    Request Status Codes DTO

    Attributes
    ----------
    allow: list[int]
        A list of allowed response codes.
    retry: list[int]
        A list of re-try-able response codes.
    reauth: list[int]
        A list of re-authorize-able response codes.
    """

    allow: list[int]
    retry: list[int]
    reauth: list[int]
