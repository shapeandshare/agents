from ........sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from ........sdk.contracts.dtos.response import Response
from ........sdk.contracts.dtos.wrapped_request import WrappedRequest
from ........sdk.contracts.types.request_verb import RequestVerbType
from ....contacts.requests.conversation_delete import ConversationDeleteRequest
from ..abstract import AbstractCommand


class ConversationDeleteCommand(AbstractCommand):
    """
    Methods
    -------
    execute(self)
        Executes the command.
    """

    async def execute(self, user_id: str, conversation_id: str) -> bool:
        """
        Executes the command.
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.DELETE,
            statuses=RequestStatusCodes(allow=[200], retry=[501, 503], reauth=[401]),
            url=f"chat-history/conversations/{conversation_id}",
            data=ConversationDeleteRequest(user_id=user_id).model_dump(),
        )
        response = await self.wrapped_request(request=wrapped_request)
        return Response[bool](data=response).data
