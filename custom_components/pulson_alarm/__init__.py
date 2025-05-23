#!/usr/local/bin python
"""
Custom integration to integrate pulson_alarm with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/pulson_alarm
"""

from __future__ import annotations

import os
from datetime import timedelta
from typing import TYPE_CHECKING

if os.getenv("HA_DEBUG", "0") == "1":
    import debugpy
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import IntegrationPulsonAlarmApiClient
from .const import (
    CONF_CLOUD_HOST,
    CONF_CLOUD_PASSWORD,
    CONF_CLOUD_PORT,
    CONF_CLOUD_USER,
    DOMAIN,
    LOGGER,
)
from .coordinator import PulsonAlarmDataUpdateCoordinator
from .data import IntegrationPulsonAlarmData
from .mqtt_client import PulsonMqttClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import IntegrationPulsonAlarmConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationPulsonAlarmConfigEntry,
) -> bool:
    """Set up the debugger."""
    if os.getenv("HA_DEBUG", "0") == "1" and not debugpy.is_client_connected():
        debugpy.listen(("0.0.0.0", 5678))  # noqa: S104 TODO:delete debugger
        debugpy.wait_for_client()
        debugpy.breakpoint()

    """Setup MQTT connection."""
    config = entry.data
    host = config["host"]
    port = int(config.get("port", 1883))
    username = config.get("username") or ""
    password = config.get("password") or ""
    serial_number = config.get("serial_number") or ""

    async def handle_message(topic: str, payload: str) -> None:
        LOGGER.info("Odebrano z MQTT: %s = %s", topic, payload)

    mqtt_client = PulsonMqttClient(
        host=host,
        username=username,
        password=password,
        serial_number=serial_number,
        port=port,
    )
    await mqtt_client.start(handle_message)
    hass.data.setdefault(DOMAIN, {})["mqtt_client"] = mqtt_client

    """Set up this integration using UI."""
    coordinator = PulsonAlarmDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=1),
    )
    entry.runtime_data = IntegrationPulsonAlarmData(
        client=IntegrationPulsonAlarmApiClient(
            host=entry.data[CONF_CLOUD_HOST],
            port=entry.data[CONF_CLOUD_PORT],
            username=entry.data[CONF_CLOUD_USER],
            password=entry.data[CONF_CLOUD_PASSWORD],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: IntegrationPulsonAlarmConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    client = hass.data[DOMAIN]["mqtt_client"]
    await client.stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: IntegrationPulsonAlarmConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
