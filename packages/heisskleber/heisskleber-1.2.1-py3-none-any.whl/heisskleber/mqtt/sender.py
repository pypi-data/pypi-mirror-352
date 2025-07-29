"""Async mqtt sink implementation."""

import asyncio
import logging
import ssl
from asyncio import CancelledError, create_task
from typing import Any, TypeVar

import aiomqtt

from heisskleber.core import Packer, Payload, Sender, json_packer
from heisskleber.core.utils import retry

from .config import MqttConf

T = TypeVar("T")


logger = logging.getLogger("heisskleber.mqtt")

MQTT_TLS_PORT = 8883


class MqttSender(Sender[T]):
    """MQTT publisher with queued message handling.

    This sink implementation provides asynchronous MQTT publishing capabilities with automatic connection management and message queueing.
    Network operations are handled in a separate task.

    Attributes:
        config: MQTT configuration in a dataclass.
        packer: Callable to pack data from type T to bytes for transport.

    """

    def __init__(self, config: MqttConf, packer: Packer[T] = json_packer) -> None:  # type: ignore[assignment]
        self.config = config
        self.packer = packer
        self._send_queue: asyncio.Queue[tuple[Payload, str, int, bool]] = asyncio.Queue(
            maxsize=config.max_saved_messages
        )
        self._sender_task: asyncio.Task[None] | None = None

    async def send(self, data: T, topic: str = "mqtt", qos: int = 0, retain: bool = False, **kwargs: Any) -> None:
        """Queue data for asynchronous publication to the mqtt broker.

        Arguments:
            data: The data to be published.
            topic: The mqtt topic to publish to.
            qos: MQTT QOS level (0, 1, or 2). Defaults to 0.o
            retain: Whether to set the MQTT retain flag. Defaults to False.
            **kwargs: Not implemented.

        Raises:
            PackerError: The data could not be serialized with the provided Packer.

        """
        if not self._sender_task:
            await self.start()

        payload = self.packer(data)
        # emulate deque behavior
        if self._send_queue.full():
            _ = self._send_queue.get_nowait()
        self._send_queue.put_nowait((payload, topic, qos, retain))

    @retry(every=5, catch=aiomqtt.MqttError, logger_fn=logger.exception)
    async def _send_work(self) -> None:
        tls_params = (
            aiomqtt.TLSParameters(
                ca_certs=None,
                certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLS,
                ciphers=None,
            )
            if self.config.ssl or self.config.port == MQTT_TLS_PORT
            else None
        )

        async with aiomqtt.Client(
            hostname=self.config.host,
            port=self.config.port,
            username=self.config.user,
            password=self.config.password,
            timeout=float(self.config.timeout),
            keepalive=self.config.keep_alive,
            will=self.config.will,
            tls_params=tls_params,
        ) as client:
            try:
                while True:
                    payload, topic, qos, retain = await self._send_queue.get()
                    await client.publish(topic=topic, payload=payload, qos=qos, retain=retain)
            except CancelledError:
                logger.info("MqttSink background loop cancelled. Emptying queue...")
                while not self._send_queue.empty():
                    _ = self._send_queue.get_nowait()
                raise

    def __repr__(self) -> str:
        """Return string representation of the MQTT sink object."""
        return f"{self.__class__.__name__}(broker={self.config.host}, port={self.config.port})"

    async def start(self) -> None:
        """Start the send queue in a separate task.

        The task will retry connections every 5 seconds on failure.
        """
        self._sender_task = create_task(self._send_work())

    async def stop(self) -> None:
        """Stop the background task."""
        if not self._sender_task:
            return
        self._sender_task.cancel()
        try:
            await self._sender_task
        except asyncio.CancelledError:
            # If the stop task was cancelled, we raise.
            task = asyncio.current_task()
            if task and task.cancelled():
                raise
        self._sender_task = None
