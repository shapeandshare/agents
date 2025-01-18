""" Health Get Command Definition """

from .......sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from .......sdk.contracts.dtos.response import Response
from .......sdk.contracts.dtos.wrapped_request import WrappedRequest
from .......sdk.contracts.types.request_verb import RequestVerbType
from ...abstract import AbstractCommand


class HealthGetCommand(AbstractCommand):
    """
    Health Get Command
    Gets the server health.

    Methods
    -------
    execute(self) -> dict
        Executes the command.
    """

    async def execute(self) -> dict:
        """
        Executes the command.

        Returns
        -------
        health: dict
            The server health (true or false).
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.GET,
            statuses=RequestStatusCodes(allow=[200], retry=[501, 503], reauth=[401]),
            url="metrics/health",
        )
        response = await self.wrapped_request(request=wrapped_request)
        return Response[dict].model_validate(response).data
