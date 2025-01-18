from ........sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from ........sdk.contracts.dtos.response import Response
from ........sdk.contracts.dtos.wrapped_request import WrappedRequest
from ........sdk.contracts.types.request_verb import RequestVerbType
from ....contacts.models.conversation import Conversation
from ....contacts.requests.conversation_message_add import ConversationMessageAddRequest
from ..abstract import AbstractCommand


class MessageAddCommand(AbstractCommand):
    """

    Methods
    -------
    execute(self)
        Executes the command.
    """

    async def execute(self, conversation_id: str, user_id: str, content: str, role: str) -> Conversation:
        """
        Executes the command.
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.POST,
            statuses=RequestStatusCodes(allow=[200], retry=[501, 503], reauth=[401]),
            url=f"chat-history/conversations/{conversation_id}/messages",
            data=ConversationMessageAddRequest(user_id=user_id, content=content, role=role).model_dump(),
        )
        response = await self.wrapped_request(request=wrapped_request)
        return Response[Conversation](data=response).data
