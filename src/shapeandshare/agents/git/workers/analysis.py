import asyncio
import logging
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from ...core.framework.contracts.dtos.service_response import ServiceResponse
from ...core.framework.contracts.events.repository import RepositoryEvent
from ...core.framework.contracts.messaging.commands.repository_analyze import RepositoryAnalyzeCommand
from ...core.infrastructure.messaging.rabbitmq.consumer import MessageConsumer
from ...core.infrastructure.messaging.rabbitmq.publisher import MessagePublisher
from ...core.services.vector.service import VectorService
from ..context import build_runtime_context, context
from ..sdk.client.git import GitAgentClient
from ..sdk.contracts.types.processing_status import ProcessingStatus
from ..services.analysis.service import AnalysisService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class AnalysisWorker(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    analysis_service: AnalysisService
    vector_service: VectorService
    text_splitter: RecursiveCharacterTextSplitter

    publisher: MessagePublisher
    consumer: MessageConsumer | None = None

    git_agent_client: GitAgentClient

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.consumer = MessageConsumer(
            config=context["rabbitmq_config"],
            message_handler=self.handle_repository_clone,
            exchange_name="git_agent",
            routing_key="repository.cloned",
            queue_name="analysis_queue",
        )

    def handle_repository_clone(self, message: dict):
        event = RepositoryEvent.model_validate(message)

        clone_command = RepositoryAnalyzeCommand(
            command_id=str(uuid4()),
            timestamp=datetime.now(),
            correlation_id=event.correlation_id,
            repository_id=event.repository_id,
            collection_id=event.collection_id,
            analysis_config={},
        )

        try:
            response: ServiceResponse = self.analysis_service.extract_repository_content(
                repository_id=event.repository_id
            )
            content: dict = response.data["content"]
            # Create context
            logger.info("putting content into vector database")
            self._create_context(col_id=clone_command.collection_id, contents=content)

            # Publish success event
            event = RepositoryEvent(
                event_id=str(uuid4()),
                event_type="REPOSITORY_ANALYZED",
                timestamp=datetime.now(),
                correlation_id=clone_command.correlation_id,
                source_service="analysis_worker",
                repository_id=clone_command.repository_id,
                collection_id=event.collection_id,
            )

            self.publisher.publish_message(
                routing_key="repository.analyzed", message=event, correlation_id=clone_command.correlation_id
            )

            # update state
            async def update_status():
                await self.git_agent_client.status_update(
                    repository_id=clone_command.repository_id, status=ProcessingStatus.COMPLETED
                )

            asyncio.run(update_status())

            # alternate implenetation
            # loop = asyncio.get_event_loop()
            # future = asyncio.run_coroutine_threadsafe(update_status(), loop)
            # future.result()

        except Exception as error:
            logger.error(f"Error handling repository clone event: {str(error)}")

            # Publish failure event
            event = RepositoryEvent(
                event_id=str(uuid4()),
                event_type="REPOSITORY_ANALYSIS_FAILED",
                timestamp=datetime.now(),
                correlation_id=clone_command.correlation_id,
                source_service="analysis_worker",
                repository_id=clone_command.repository_id,
                collection_id=clone_command.collection_id,
                error_details=str(error),
            )

            self.publisher.publish_message(
                routing_key="repository.failed", message=event, correlation_id=clone_command.correlation_id
            )

    def start(self):
        self.consumer.start_consuming()

    def stop(self):
        self.consumer.stop_consuming()

    def _create_context(self, col_id: str, contents: dict) -> None:
        # determine if we need to reload the data

        # Create collection. get_collection, get_or_create_collection, delete_collection also available!
        collection = self.vector_service.client.create_collection(name=col_id)

        for key, value in contents.items():
            doc: str = (
                "<document>\n"
                "<source>"
                f"{key}"
                "</source>\n"
                "<document_content>\n"
                f"{value}"
                "</document_content>\n"
                "</document>"
            )
            new_doc: Document = Document(page_content=doc)
            all_splits: list[Document] = self.text_splitter.split_documents([new_doc])
            all_docs: list[str] = [str(doc) for doc in all_splits]

            # /Users/joshburt/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz
            # https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
            # https://cookbook.chromadb.dev/faq/#valueerror-you-must-provide-an-embedding-function-to-compute-embeddings
            collection.add(documents=all_docs, ids=[f"{key}-{i}" for i in range(len(all_splits))])


def main():
    """Main worker entrypoint"""
    load_dotenv(dotenv_path=".env", verbose=True)

    logger.info("Initializing context")

    build_runtime_context()
    logger.info("Done initializing context")

    worker: AnalysisWorker = AnalysisWorker(
        analysis_service=context["analysis_service"],
        vector_service=context["vector_service"],
        publisher=context["publisher"],
        text_splitter=context["text_splitter"],
        git_agent_client=context["git_agent_client"],
    )

    logger.info("Consuming messages from queue")
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == "__main__":
    main()
