import asyncio
from typing import Generic, TypeVar

import jsons
from ed_domain.common.logging import get_logger
from ed_domain.documentation.message_queue.rabbitmq.abc_queue_producer import \
    ABCQueueProducer
from pika import BasicProperties
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.channel import Channel
from pika.connection import URLParameters

LOG = get_logger()
TRequestModel = TypeVar("TRequestModel")


class RabbitMQProducer(Generic[TRequestModel], ABCQueueProducer[TRequestModel]):
    def __init__(
        self, url: str, queue: str, loop: asyncio.AbstractEventLoop | None = None
    ):
        self._url = url
        self._queue = queue
        self._loop = loop

        self._connection: AsyncioConnection | None = None
        self._channel: Channel | None = None
        self._ready_event = asyncio.Event()

    async def start(self) -> None:
        LOG.info("Starting RabbitMQ producer...")
        try:
            parameters = URLParameters(self._url)
            self._connection = AsyncioConnection(
                parameters,
                on_open_callback=self._on_connection_open,
                on_open_error_callback=self._on_connection_error,
                on_close_callback=self._on_connection_closed,
                custom_ioloop=self._loop,
            )
            await self._ready_event.wait()
        except Exception as e:
            LOG.error(f"Failed to connect/start producer: {e}")
            raise

    async def publish(self, request: TRequestModel) -> None:
        if not self._channel or not self._channel.is_open:
            LOG.error("Channel is not open. Cannot publish.")
            raise RuntimeError("RabbitMQ channel is not open.")

        try:
            serialized_message = jsons.dumps(request)
            self._channel.basic_publish(
                exchange="",
                routing_key=self._queue,
                body=serialized_message,
                properties=BasicProperties(delivery_mode=2),  # Persistent
            )
            LOG.info(f"Published message to {self._queue}")
            LOG.debug(f"Payload: {serialized_message[:200]}...")

        except Exception as e:
            LOG.error(f"Failed to publish message: {e}")
            raise

    def stop(self) -> None:
        LOG.info("Stopping RabbitMQ producer...")
        if self._connection and self._connection.is_open:
            self._connection.close()

    def _on_connection_open(self, connection: AsyncioConnection) -> None:
        LOG.info("Connection opened")
        self._connection = connection
        self._connection.channel(on_open_callback=self._on_channel_open)

    def _on_channel_open(self, channel: Channel) -> None:
        LOG.info("Channel opened")
        self._channel = channel
        self._channel.queue_declare(
            queue=self._queue, durable=True, callback=self._on_queue_declared
        )

    def _on_queue_declared(self, frame) -> None:
        LOG.info(f"Queue declared: {self._queue}")
        self._ready_event.set()

    def _on_connection_error(self, _unused_connection, error):
        LOG.error(f"Connection error: {error}")
        self._ready_event.set()

    def _on_connection_closed(self, connection, reason):
        LOG.warning(f"Connection closed: {reason}")
        self._ready_event.clear()
