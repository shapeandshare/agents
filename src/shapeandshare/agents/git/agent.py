import logging
from datetime import datetime
from uuid import uuid4

from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.framework.contracts.events.repository import RepositoryEvent
from ..core.framework.interfaces.agent import BaseAgent
from ..core.infrastructure.messaging.rabbitmq.publisher import MessagePublisher
from ..core.infrastructure.persistence.chromadb.utils import ChromaUtils
from ..core.services.chathistory.sdk.contacts.models.conversation import Conversation
from .sdk.contracts.dtos.chat import BaseChatRequest, ChatRequest
from .sdk.contracts.dtos.git_metadata import GitMetadata
from .sdk.contracts.types.processing_status import ProcessingStatus
from .services.analysis.service import AnalysisService
from .services.metadata.service import MetadataService
from .services.repository.service import RepositoryService

logger = logging.getLogger()


class GitAgent(BaseAgent):
    class Config:
        arbitrary_types_allowed = True

    """ """

    repository_service: RepositoryService
    analysis_service: AnalysisService
    metadata_service: MetadataService
    text_splitter: RecursiveCharacterTextSplitter
    publisher: MessagePublisher

    async def process_repository(self, request: BaseChatRequest) -> GitMetadata:
        if not ChromaUtils.exists(
            vector_service=self.vector_service, metadata_service=self.metadata_service, request=request
        ):
            logger.info("beginning repository ingestion")
            conversation: Conversation = await self.chathistory_client.conversation_create(user_id=request.id)
            chat_request: ChatRequest = ChatRequest.model_validate(
                {
                    **request.model_dump(),
                    "conversation_id": conversation.id,
                    "prompt": "",
                    "k": 0,
                }  # prompt, and k is currently required but not used in this condition
            )
            metadata: GitMetadata = self.metadata_service.create(request=chat_request)

            # update state
            self.metadata_service.update(request=request, metadata_partial={"status": ProcessingStatus.PROCESSING})

            # try:
            event_id: str = str(uuid4())
            event = RepositoryEvent(
                event_id=event_id,
                event_type="REPOSITORY_PROCESS",
                timestamp=datetime.now(),
                correlation_id=event_id,
                source_service="git_agent",
                repository_id=metadata.id,
                collection_id=metadata.col_id,
                url=request.url,
            )
            self.publisher.publish_message(message=event, routing_key="repository.process")
            # finally:
            #     self.publisher.close()
            return metadata

    async def generate_chat_response(self, request: ChatRequest) -> dict:
        metadata: GitMetadata | None = self.metadata_service.get(request=BaseChatRequest.model_validate((request)))
        if metadata and metadata.status in [ProcessingStatus.COMPLETED] and metadata.col_id:
            vectorstore: Chroma = self._load_context(collection_id=metadata.col_id)

            # add conversation id to request
            request.conversation_id = metadata.conversation_id

            # Generate response
            response = await self.generate_response(vectorstore=vectorstore, request=request)
            return response

        if metadata is None:
            msg: str = "Context does not exist"
        else:
            msg: str = f"Context not ready, current state is ({metadata.status})"
        raise Exception(msg)

    async def delete_context(self, request: BaseChatRequest) -> None:
        if ChromaUtils.exists(
            vector_service=self.vector_service, metadata_service=self.metadata_service, request=request
        ):
            metadata: GitMetadata = self.metadata_service.get(request=request)

            self.vector_service.client.delete_collection(name=metadata.col_id)
            self.metadata_service.delete(request=request)
            await self.chathistory_client.conversation_delete(
                conversation_id=metadata.conversation_id, user_id=metadata.id
            )

    def _load_context(self, collection_id: str) -> Chroma:
        return self.vector_service.get_vectorstore(collection_id=collection_id)
