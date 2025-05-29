"""Sample API Client."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout

from pulson_alarm.const import CONF_USER_DEFAULT_CODE

if TYPE_CHECKING:
    from collections.abc import Callable

    from pulson_alarm.mqtt_client import PulsonMqttClient


class IntegrationPulsonAlarmApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntegrationPulsonAlarmApiClientCommunicationError(
    IntegrationPulsonAlarmApiClientError,
):
    """Exception to indicate a communication error."""


class IntegrationPulsonAlarmApiClientAuthenticationError(
    IntegrationPulsonAlarmApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise IntegrationPulsonAlarmApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class IntegrationPulsonAlarmApiClient:
    """Sample API Client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        mqtt_client: PulsonMqttClient,
    ) -> None:
        """Sample API Client."""
        self._session = session
        self._mqtt_client = mqtt_client
        self._inputs: dict[str, dict] = {}
        self._partitions: dict[str, dict] = {}
        self._entity_update_callbacks: list[Callable[[], None]] = []
        self._input_added_callbacks: list[Callable[[str], None]] = []
        self._partition_added_callbacks: list[Callable[[str], None]] = []

    def entity_register_update_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback to be called when input data is updated.

        The callback is typically used to notify Home Assistant that
        new data is available and entities should update their state.
        """
        self._entity_update_callbacks.append(callback)

    def input_register_added_callback(self, callback: Callable[[str], None]) -> None:
        """
        Register a callback to be called when a new input (e.g., alarm line) is added.

        The callback receives the input ID (as a string) of the newly added input.
        This is typically used to dynamically create new entities in Home Assistant
        when new inputs appear during runtime.
        """
        self._input_added_callbacks.append(callback)

    def input_update_param(self, input_id: str, key: str, value: Any) -> None:
        """
        Update a parameter for a specific input.

        If the input ID is not known, registered 'input added' callbacks are invoked.
        Then the value for the specified key is updated (or added).
        Finally, all registered 'input update' callbacks are called to notify the system
        (e.g., trigger entity updates in Home Assistant).
        """
        if input_id not in self._inputs:
            for cb in self._input_added_callbacks:
                cb(input_id)
        if input_id not in self._inputs:
            self._inputs[input_id] = {}
        self._inputs[input_id][key] = value
        for cb in self._entity_update_callbacks:
            cb()

    def input_get_state(self, input_id: str) -> dict:
        """Get the current state (parameter dictionary) of a specific input."""
        return self._inputs.get(input_id, {})

    def input_get_all_ids(self) -> list:
        """Get a list of all registered input IDs."""
        return list(self._inputs)

    @property
    def inputs(self) -> dict[str, dict]:
        """Return the full internal dictionary of all inputs and their parameters."""
        return self._inputs

    async def set_input_block_state(self, input_id: str, *, block: bool) -> None:
        """Change blockade state in API and send to MQTT."""
        topic = f"inputs/{input_id}/block_set"
        payload = (
            f"{CONF_USER_DEFAULT_CODE}1" if block else f"{CONF_USER_DEFAULT_CODE}0"
        )
        await self._mqtt_client.publish(topic, payload, retain=True)
        self.input_update_param(input_id, "block", int(block))

    def partition_register_added_callback(
        self, callback: Callable[[str], None]
    ) -> None:
        """
        Register a callback to be called when a new partition  is added.

        The callback receives the ID (as a string) of the newly added partition.
        This is typically used to dynamically create new entities in Home Assistant
        when new inputs appear during runtime.
        """
        self._partition_added_callbacks.append(callback)

    def partition_update_param(self, partition_id: str, key: str, value: Any) -> None:
        """
        Update a parameter for a specific partition.

        If the ID is not known, registered callbacks are invoked.
        Then the value for the specified key is updated (or added).
        Finally, all registered 'update' callbacks are called to notify the system
        """
        if partition_id not in self._partitions:
            for cb in self._partition_added_callbacks:
                cb(partition_id)
        if partition_id not in self._partitions:
            self._partitions[partition_id] = {}
        self._partitions[partition_id][key] = value
        for cb in self._entity_update_callbacks:
            cb()

    def partition_get_state(self, partition_id: str) -> dict:
        """Get the current state (parameter dictionary) of a specific partition."""
        return self._partitions.get(partition_id, {})

    def partition_get_all_ids(self) -> list:
        """Get a list of all registered partition IDs."""
        return list(self._partitions)

    @property
    def partitions(self) -> dict[str, dict]:
        """Return the full dictionary of all partitions and their parameters."""
        return self._partitions

    async def partition_arm(self, partition_id: str) -> None:
        """Arm partition, send to MQTT."""
        topic = f"partitions/{partition_id}/set_arm"
        payload = f"{CONF_USER_DEFAULT_CODE}1"
        await self._mqtt_client.publish(topic, payload, retain=False)

    async def partition_disarm(self, partition_id: str) -> None:
        """Disarm partition, send to MQTT."""
        topic = f"partitions/{partition_id}/set_disarm"
        payload = f"{CONF_USER_DEFAULT_CODE}0"
        await self._mqtt_client.publish(topic, payload, retain=False)

    async def partition_arm_night(self, partition_id: str) -> None:
        """Night arm partition, send to MQTT."""
        topic = f"partitions/{partition_id}/set_arm"
        payload = f"{CONF_USER_DEFAULT_CODE}2"
        await self._mqtt_client.publish(topic, payload, retain=False)

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise IntegrationPulsonAlarmApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise IntegrationPulsonAlarmApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise IntegrationPulsonAlarmApiClientError(
                msg,
            ) from exception
