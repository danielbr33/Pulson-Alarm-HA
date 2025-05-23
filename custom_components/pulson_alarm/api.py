#!/usr/local/bin python
"""Sample API Client."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout

if TYPE_CHECKING:
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
