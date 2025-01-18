""" Command Options Definition """

from pydantic import BaseModel


class CommandOptions(BaseModel):
    """
    Command Options DTO

    Attributes
    ----------
    sleep_time: float
        Sleep time in seconds.
    retry_count: int
        Maximum number of retries.
    tld: str
        Top Level Domain to work within
    timeout: float
        Time out in seconds.
    """

    sleep_time: float
    retry_count: int
    tld: str
    scheme: str
    timeout: float
