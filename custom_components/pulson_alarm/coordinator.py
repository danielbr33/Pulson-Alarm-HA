"""DataUpdateCoordinator for pulson_alarm."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    IntegrationPulsonAlarmApiClient,
    IntegrationPulsonAlarmApiClientAuthenticationError,
    IntegrationPulsonAlarmApiClientError,
)

if TYPE_CHECKING:
    from datetime import timedelta
    from logging import Logger

    from homeassistant.core import HomeAssistant

    from .data import IntegrationPulsonAlarmConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class PulsonAlarmDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        name: str,
        update_interval: timedelta,
        api_client: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=logger,
            name=name,
            update_interval=update_interval,
        )
        self.api_client = api_client

    config_entry: IntegrationPulsonAlarmConfigEntry

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.api_client.async_get_data()
        except IntegrationPulsonAlarmApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except IntegrationPulsonAlarmApiClientError as exception:
            raise UpdateFailed(exception) from exception
