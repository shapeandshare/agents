import logging
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from pydantic import BaseModel

from ...core.framework.contracts.events.repository import RepositoryEvent
from ...core.framework.contracts.messaging.commands.repository_clone import RepositoryCloneCommand
from ...core.framework.contracts.messaging.commands.repository_delete import RepositoryDeleteCommand
from ...core.infrastructure.messaging.rabbitmq.consumer import MessageConsumer
from ...core.infrastructure.messaging.rabbitmq.publisher import MessagePublisher
from ..context import build_runtime_context, context
from ..services.repository.service import RepositoryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


class RepositoryWorker(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    repository_service: RepositoryService
    publisher: MessagePublisher
    consumer_clone: MessageConsumer | None = None
    consumer_delete: MessageConsumer | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.consumer_clone = MessageConsumer(
            config=context["rabbitmq_config"],
            message_handler=self.handle_repository_clone,
            exchange_name="git_agent",
            routing_key="repository.process",
            queue_name="repository_clone_queue",
        )

        self.consumer_delete = MessageConsumer(
            config=context["rabbitmq_config"],
            message_handler=self.handle_repository_delete,
            exchange_name="git_agent",
            routing_key="repository.analyzed",
            queue_name="repository_delete_queue",
        )

    def handle_repository_clone(self, message: dict):
        event = RepositoryEvent.model_validate(message)

        clone_command = RepositoryCloneCommand(
            command_id=str(uuid4()),
            timestamp=datetime.now(),
            correlation_id=event.correlation_id,
            repository_id=event.repository_id,
            collection_id=event.collection_id,
            url=event.url,
        )

        try:
            self.repository_service.clone(url=event.url, repository_id=event.repository_id)

            # Publish success event
            event = RepositoryEvent(
                event_id=str(uuid4()),
                event_type="REPOSITORY_CLONED",
                timestamp=datetime.now(),
                correlation_id=clone_command.correlation_id,
                source_service="repository_worker",
                repository_id=clone_command.repository_id,
                collection_id=clone_command.collection_id,
                url=clone_command.url,
            )

            self.publisher.publish_message(
                routing_key="repository.cloned", message=event, correlation_id=clone_command.correlation_id
            )

        except Exception as error:
            logger.error(f"Error handling repository clone event: {str(error)}")

            # Publish failure event
            event = RepositoryEvent(
                event_id=str(uuid4()),
                event_type="REPOSITORY_CLONE_FAILED",
                timestamp=datetime.now(),
                correlation_id=clone_command.correlation_id,
                source_service="repository_worker",
                repository_id=clone_command.repository_id,
                collection_id=clone_command.collection_id,
                url=clone_command.url,
                error_details=str(error),
            )

            self.publisher.publish_message(
                routing_key="repository.failed", message=event, correlation_id=clone_command.correlation_id
            )

    def handle_repository_delete(self, message: dict):
        event = RepositoryEvent.model_validate(message)

        delete_command = RepositoryDeleteCommand(
            command_id=str(uuid4()),
            timestamp=datetime.now(),
            correlation_id=event.correlation_id,
            repository_id=event.repository_id,
        )

        try:
            self.repository_service.delete(repository_id=event.repository_id)

            # Publish success event
            event = RepositoryEvent(
                event_id=str(uuid4()),
                event_type="REPOSITORY_DELETED",
                timestamp=datetime.now(),
                correlation_id=delete_command.correlation_id,
                source_service="repository_worker",
                repository_id=delete_command.repository_id,
            )

            self.publisher.publish_message(
                routing_key="repository.deleted", message=event, correlation_id=delete_command.correlation_id
            )

        except Exception as error:
            logger.error(f"Error handling repository clone event: {str(error)}")

            # Publish failure event
            event = RepositoryEvent(
                event_id=str(uuid4()),
                event_type="REPOSITORY_DELETE_FAILED",
                timestamp=datetime.now(),
                correlation_id=delete_command.correlation_id,
                source_service="repository_worker",
                repository_id=delete_command.repository_id,
                collection_id=delete_command.collection_id,
                error_details=str(error),
            )

            self.publisher.publish_message(
                routing_key="repository.failed", message=event, correlation_id=delete_command.correlation_id
            )

    def start(self):
        self.consumer_clone.start_consuming()
        self.consumer_delete.start_consuming()

    def stop(self):
        self.consumer_clone.stop_consuming()
        self.consumer_delete.stop_consuming()


def main():
    """Main worker entrypoint"""
    load_dotenv(dotenv_path=".env", verbose=True)

    logger.info("Initializing context")

    build_runtime_context()
    logger.info("Done initializing context")

    worker: RepositoryWorker = RepositoryWorker(
        repository_service=context["repository_service"], publisher=context["publisher"]
    )

    logger.info("Consuming messages from queue")
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()


if __name__ == "__main__":
    main()
