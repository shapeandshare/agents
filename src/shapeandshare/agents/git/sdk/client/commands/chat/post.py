from ......sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from ......sdk.contracts.dtos.response import Response
from ......sdk.contracts.dtos.wrapped_request import WrappedRequest
from ......sdk.contracts.types.request_verb import RequestVerbType
from ....contracts.dtos.chat import ChatRequest
from ..abstract import AbstractCommand


class ChatCommand(AbstractCommand):
    """
    Methods
    -------
    execute(self)
        Executes the command.
    """

    async def execute(self, request: ChatRequest) -> dict:
        """
        Executes the command.
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.POST,
            statuses=RequestStatusCodes(allow=[200], retry=[501, 503], reauth=[401]),
            url="git/question",
            data=request.model_dump(),
        )
        response: dict = await self.wrapped_request(request=wrapped_request)
        return Response[dict].model_validate(response).data
