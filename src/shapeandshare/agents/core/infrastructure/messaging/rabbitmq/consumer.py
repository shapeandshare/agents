import json
import logging
from typing import Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pydantic import BaseModel

from ....framework.contracts.dtos.rabbitmq_config import RabbitMQConfig

logger = logging.getLogger()


class MessageConsumer(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    config: RabbitMQConfig
    message_handler: Callable
    exchange_name: str
    routing_key: str
    queue_name: str

    connection: pika.BlockingConnection | None = None
    channel: BlockingChannel | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_connection()
        self._setup_queues()

    def _setup_connection(self):
        credentials = pika.PlainCredentials(username=self.config.username, password=self.config.password)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.config.hostname, port=self.config.port, credentials=credentials)
        )

        self.channel = self.connection.channel()

        # Main exchange
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="topic", durable=True)

        # DLQ exchange
        self.channel.exchange_declare(exchange=f"{self.exchange_name}.dlq", exchange_type="topic", durable=True)

    def _setup_queues(self):
        """Setup main queue and DLQ"""
        # Main queue
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            # arguments={
            #     "x-dead-letter-exchange": f"{self.exchange_name}.dlq",
            #     "x-dead-letter-routing-key": f"{self.routing_key}.dlq",
            # },
        )

        # # DLQ queue
        # self.channel.queue_declare(queue=f"{self.queue_name}.dlq", durable=True)

        # Bind queues
        self.channel.queue_bind(queue=self.queue_name, exchange=self.exchange_name, routing_key=self.routing_key)

        # self.channel.queue_bind(
        #     queue=f"{self.queue_name}.dlq",
        #     exchange=f"{self.exchange_name}.dlq",
        #     routing_key=f"{self.routing_key}.dlq",
        # )

    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self._process_message)

        logger.info(f"Starting to consume from queue: {self.queue_name}")
        self.channel.start_consuming()

    def stop_consuming(self):
        if self.channel and not self.channel.is_closed:
            self.channel.stop_consuming()

        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def _process_message(
        self,
        channel: BlockingChannel,
        method,
        # method: Basic.Deliver,
        properties,
        # properties: BasicProperties,
        body: bytes,
    ):
        """Process message with retry logic"""

        headers = properties.headers or {}
        retry_count = headers.get("retry_count", 0)

        try:
            # Process message
            message = json.loads(body)
            self.message_handler(message)

            # Acknowledge successful processing
            channel.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

            # Handle retry logic
            if retry_count < headers.get("max_retries", 3):
                headers["retry_count"] = retry_count + 1

                # Republish with incremented retry count
                channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=headers.get("original_routing_key"),
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        message_id=properties.message_id,
                        correlation_id=properties.correlation_id,
                        headers=headers,
                    ),
                )

                # Acknowledge the original message
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Move to DLQ
                channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
