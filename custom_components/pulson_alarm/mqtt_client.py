"""Class handling MQTT connection."""

from __future__ import annotations

import asyncio
import ssl
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

from asyncio_mqtt import Client, MqttError

from .const import LOGGER


class PulsonMqttClient:
    """Handler of MQTT connection."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        serial_number: str,
        port: int = 8883,
    ) -> None:
        """Set data needed to establish connection."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.serial_number = serial_number
        self._connected = False

        tls_context = ssl.create_default_context()
        self._client = Client(
            hostname=host,
            port=port,
            username=username,
            password=password,
            tls_context=tls_context,
            keepalive=60,
        )
        self._task = None
        self._running = False

    async def start(
        self,
        on_message: Callable[[str, str], Awaitable[None]] | None,
    ) -> None:
        """Connect to MQTT."""

        async def _reader() -> None:
            """Connect to MQTT."""
            try:
                async with self._client.messages() as messages:
                    try:
                        await self._client.connect()
                        self._connected = True
                    except MqttError as e:
                        LOGGER.error("Error MQTT connection: code %s", e)
                        LOGGER.error(
                            "host: %s, port: %s, user: %s",
                            self._host,
                            self._port,
                            self._username,
                        )
                        return
                    await self._client.subscribe(f"system/{self.serial_number}/#")
                    LOGGER.info("MQTT subscribed to alarm/#")
                    async for message in messages:
                        if isinstance(message.payload, bytes):
                            payload = message.payload.decode()
                        else:
                            payload = str(message.payload)
                        if isinstance(message.topic, bytes):
                            topic = message.topic.decode()
                        else:
                            topic = str(message.topic)
                        LOGGER.debug("MQTT received: %s -> %s", topic, payload)
                        if on_message is not None:
                            await on_message(topic, payload)
            except MqttError as err:
                LOGGER.error("MQTT error: %s", err)
                self._connected = True
                return

        self._running = True
        self._task = asyncio.create_task(_reader())
        await asyncio.sleep(0.5)
        if not self._connected:
            msg = "Failed to connect to MQTT"
            raise MqttError(msg)

    async def stop(self) -> None:
        """Disconnect MQTT."""
        self._running = False
        if self._task:
            self._task.cancel()
        await self._client.disconnect()

    async def publish(
        self, topic: str, payload: str, *, retain: bool = False, qos: int = 0
    ) -> None:
        """
        Publish a message to the MQTT broker.

        Args:
            topic: Topic string to publish to.
            payload: Payload to send.
            retain: Whether the message should be retained.
            qos: Quality of Service level (0, 1, or 2).

        """
        if not self._connected:
            LOGGER.warning("Attempted to publish while MQTT is disconnected.")
            return
        try:
            topic = f"system/{self.serial_number}/{topic}"
            await self._client.publish(topic, payload, qos=qos, retain=retain)
            LOGGER.debug("MQTT published: %s -> %s", topic, payload)
        except MqttError as e:
            LOGGER.error("Failed to publish MQTT message: %s", e)
