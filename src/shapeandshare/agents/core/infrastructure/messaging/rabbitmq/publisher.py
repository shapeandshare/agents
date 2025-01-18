import logging
from uuid import uuid4

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pydantic import BaseModel

from ....framework.contracts.dtos.rabbitmq_config import RabbitMQConfig

logger = logging.getLogger()


class MessagePublisher(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    config: RabbitMQConfig
    exchange_name: str
    max_retries: int = 3
    retry_delay: int = 5000

    channel: BlockingChannel | None = None
    connection: pika.BlockingConnection | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_connection()
        self._setup_exchanges()

    def on_connection_close(self):
        msg: str = "Connection closed, reconnecting ..."
        logger.warning(msg)
        self._setup_connection()

    def _setup_connection(self):
        logger.info("Setting up connection to RabbitMQ")
        credentials = pika.PlainCredentials(username=self.config.username, password=self.config.password)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.config.hostname, port=self.config.port, credentials=credentials, heartbeat=60
            )
        )

        self.channel = self.connection.channel()

        # Declare exchange
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="topic", durable=True)
        logger.info("Connected to RabbitMQ")

    def _setup_exchanges(self):
        """Setup main exchange and DLQ exchange"""
        # Main exchange
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="topic", durable=True)

        # DLQ exchange
        self.channel.exchange_declare(exchange=f"{self.exchange_name}.dlq", exchange_type="topic", durable=True)

    def publish_message(self, routing_key: str, message: BaseModel, correlation_id: str | None = None) -> None:
        """Publish message with headers and DLQ support"""
        try:
            message_id = str(uuid4())
            headers = {"retry_count": 0, "max_retries": self.max_retries, "original_routing_key": routing_key}

            try:
                # if self.channel.is_open:
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=routing_key,
                    body=message.model_dump_json(),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                        message_id=message_id,
                        correlation_id=correlation_id or message_id,
                        content_type="application/json",
                        headers=headers,
                    ),
                )
                logger.info(f"Published message {message_id} to {routing_key}")
            # else:
            except Exception as error:
                logger.warning("Channel is closed")
                logger.warning(str(error))
                self.on_connection_close()
                self.publish_message(routing_key=routing_key, message=message, correlation_id=correlation_id)

        except Exception as error:
            logger.error(f"Error publishing message: {str(error)}")
            raise error

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
