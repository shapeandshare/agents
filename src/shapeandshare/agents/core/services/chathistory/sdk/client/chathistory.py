from ......sdk.contracts.dtos.command_options import CommandOptions
from ..contacts.models.conversation import Conversation
from ..contacts.models.conversation_summary import ConversationSummary
from .commands.conversation.create import ConversationCreateCommand
from .commands.conversation.delete import ConversationDeleteCommand
from .commands.conversation.get import ConversationGetCommand
from .commands.conversation.list import ConversationsListCommand
from .commands.message.add import MessageAddCommand
from .commands.metrics.health.get import HealthGetCommand


class ChatHistoryClient:
    """ """

    # metrics/health
    health_get_command: HealthGetCommand

    # Conversations
    conversation_create_command: ConversationCreateCommand
    conversation_delete_command: ConversationDeleteCommand
    conversations_list_command: ConversationsListCommand
    conversation_get_command: ConversationGetCommand

    # Messages
    message_add_command: MessageAddCommand

    def __init__(self, options: CommandOptions | None = None):
        command_dict: dict = {}
        if options:
            command_dict["options"] = options

        ### metrics
        self.health_get_command = HealthGetCommand.model_validate(command_dict)

        ### conversations
        self.conversation_create_command = ConversationCreateCommand.model_validate(command_dict)
        self.conversation_delete_command = ConversationDeleteCommand.model_validate(command_dict)
        self.conversations_list_command = ConversationsListCommand.model_validate(command_dict)
        self.conversation_get_command = ConversationGetCommand.model_validate(command_dict)

        ### messages
        self.message_add_command = MessageAddCommand.model_validate(command_dict)

    async def health_get(self) -> dict:
        """
        Gets the server health.

        Returns
        -------
        health: dict
            The server health (true or false).
        """

        return await self.health_get_command.execute()

    async def conversation_create(self, user_id: str) -> Conversation:
        """"""
        return await self.conversation_create_command.execute(user_id=user_id)

    async def conversation_delete(self, conversation_id: str, user_id: str) -> bool:
        """"""
        return await self.conversation_delete_command.execute(conversation_id=conversation_id, user_id=user_id)

    async def conversations_list(self, user_id: str, limit: int = 10, offset: int = 0) -> list[ConversationSummary]:
        """"""
        return await self.conversations_list_command.execute(user_id=user_id, limit=limit, offset=offset)

    async def conversation_get(self, conversation_id: str, user_id: str) -> Conversation:
        """"""
        return await self.conversation_get_command.execute(conversation_id=conversation_id, user_id=user_id)

    async def message_add(self, conversation_id: str, user_id: str, content: str, role: str) -> Conversation:
        """ """
        return await self.message_add_command.execute(
            conversation_id=conversation_id, user_id=user_id, content=content, role=role
        )
