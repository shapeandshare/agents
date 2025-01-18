from ........sdk.contracts.dtos.request_status_codes import RequestStatusCodes
from ........sdk.contracts.dtos.response import Response
from ........sdk.contracts.dtos.wrapped_request import WrappedRequest
from ........sdk.contracts.types.request_verb import RequestVerbType
from ....contacts.models.conversation_summary import ConversationSummary
from ....contacts.requests.conversations_get import ConversationsGetRequest
from ..abstract import AbstractCommand


class ConversationsListCommand(AbstractCommand):
    """
    Methods
    -------
    execute(self)
        Executes the command.
    """

    async def execute(self, user_id: str, limit: int = 10, offset: int = 0) -> list[ConversationSummary]:
        """
        Executes the command.
        """

        wrapped_request: WrappedRequest = WrappedRequest(
            verb=RequestVerbType.GET,
            statuses=RequestStatusCodes(allow=[200], retry=[501, 503], reauth=[401]),
            url=f"chat-history/users/{user_id}/conversations",
            data=ConversationsGetRequest(limit=limit, offset=offset).model_dump(),
        )
        response = await self.wrapped_request(request=wrapped_request)
        return Response[list[ConversationSummary]](data=response).data
