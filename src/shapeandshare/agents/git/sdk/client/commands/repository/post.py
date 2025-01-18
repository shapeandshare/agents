from ......sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from ......sdk.contracts.dtos.response import Response
from ......sdk.contracts.dtos.wrapped_request import WrappedRequest
from ......sdk.contracts.types.request_verb import RequestVerbType
from ....contracts.dtos.chat import BaseChatRequest
from ....contracts.dtos.git_metadata import GitMetadata
from ..abstract import AbstractCommand


class RepositoryPostCommand(AbstractCommand):
    """
    Methods
    -------
    execute(self)
        Executes the command.
    """

    async def execute(self, request: BaseChatRequest) -> GitMetadata:
        """
        Executes the command.
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.POST,
            statuses=RequestStatusCodes(allow=[202], retry=[501, 503], reauth=[401]),
            url="git",
            data=request.model_dump(),
        )
        response = await self.wrapped_request(request=wrapped_request)
        return Response[GitMetadata].model_validate(response).data
