from ........sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from ........sdk.contracts.dtos.response import Response
from ........sdk.contracts.dtos.wrapped_request import WrappedRequest
from ........sdk.contracts.types.request_verb import RequestVerbType
from ....contacts.models.conversation import Conversation
from ....contacts.requests.conversation_get import ConversationGetRequest
from ..abstract import AbstractCommand


class ConversationGetCommand(AbstractCommand):
    """
    Methods
    -------
    execute(self)
        Executes the command.
    """

    async def execute(self, conversation_id: str, user_id: str) -> Conversation:
        """
        Executes the command.
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.GET,
            statuses=RequestStatusCodes(allow=[200], retry=[501, 503], reauth=[401]),
            url=f"chat-history/conversations/{conversation_id}",
            data=ConversationGetRequest(user_id=user_id).model_dump(),
        )
        response = await self.wrapped_request(request=wrapped_request)
        return Response[Conversation](data=response).data
