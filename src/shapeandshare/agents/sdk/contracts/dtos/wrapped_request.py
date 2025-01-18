""" Wrapped Request Definition """

from pydantic import BaseModel

from ..types.request_verb import RequestVerbType
from .request_status_codes import RequestStatusCodes


class WrappedRequest(BaseModel):
    """
    Wrapped Request DTO

    Attributes
    ----------
    verb: RequestVerbType
        The verb of the REST API request.
    statuses: RequestStatusCodes
        The status code assignments for response handling.
    url: str
        The complete url to call
    data: dict | None  # str or dict - needs confirmation
        Either form data or body (based on type - see requests documentation)
    params: dict[str, str] | None
        Query parameters
    """

    verb: RequestVerbType
    statuses: RequestStatusCodes
    url: str
    data: dict | None = None
    params: dict[str, str] | None = None
