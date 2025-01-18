from ....sdk.contracts.dtos.command_options import CommandOptions
from ..contracts.dtos.chat import BaseChatRequest, ChatRequest
from ..contracts.dtos.git_metadata import GitMetadata
from ..contracts.dtos.status_update import RepositoryStatusUpdateRequest
from ..contracts.types.processing_status import ProcessingStatus
from .commands.chat.post import ChatCommand
from .commands.metrics.health.get import HealthGetCommand
from .commands.repository.delete import RepositoryDeleteCommand
from .commands.repository.post import RepositoryPostCommand
from .commands.repository.put import RepositoryPutCommand


class GitAgentClient:
    """ """

    # metrics/health
    health_get_command: HealthGetCommand

    # repository
    repository_put_command: RepositoryPutCommand
    repository_post_command: RepositoryPostCommand
    repository_delete_command: RepositoryDeleteCommand

    # chat
    chat_command: ChatCommand

    def __init__(self, options: CommandOptions | None = None):
        command_dict: dict = {}
        if options:
            command_dict["options"] = options

        ### metrics
        self.health_get_command = HealthGetCommand.model_validate(command_dict)

        # repository
        self.repository_put_command = RepositoryPutCommand.model_validate(command_dict)
        self.repository_post_command = RepositoryPostCommand.model_validate(command_dict)
        self.repository_delete_command = RepositoryDeleteCommand.model_validate(command_dict)

        # chat
        self.chat_command = ChatCommand.model_validate(command_dict)

    async def health_get(self) -> dict:
        """
        Gets the server health.

        Returns
        -------
        health: dict
            The server health (true or false).
        """

        return await self.health_get_command.execute()

    async def status_update(self, repository_id: str, status: ProcessingStatus) -> GitMetadata:
        request: RepositoryStatusUpdateRequest = RepositoryStatusUpdateRequest(
            repository_id=repository_id, status=status
        )
        return await self.repository_put_command.execute(request=request)

    async def repository_delete(self, user_id: str, repository_url: str) -> None:
        request: BaseChatRequest = BaseChatRequest(id=user_id, url=repository_url)
        await self.repository_delete_command.execute(request=request)

    async def repository_ingest(self, user_id: str, repository_url: str) -> GitMetadata:
        request: BaseChatRequest = BaseChatRequest(id=user_id, url=repository_url)
        return await self.repository_post_command.execute(request=request)

    async def chat(self, user_id: str, repository_url: str, prompt: str, k: int = 16) -> dict:
        request: ChatRequest = ChatRequest(id=user_id, url=repository_url, prompt=prompt, k=k)
        return await self.chat_command.execute(request=request)
