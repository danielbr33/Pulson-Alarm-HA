"""
Custom integration to integrate pulson_alarm with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/pulson_alarm
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if os.getenv("HA_DEBUG", "0") == "1":
    import debugpy
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.panel_custom import async_register_panel
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.http import HomeAssistantView
from homeassistant.loader import async_get_loaded_integration

from .api import IntegrationPulsonAlarmApiClient
from .const import (
    CLOUD_TOPIC_ACTION_INDEX,
    CLOUD_TOPIC_MODULE_INDEX,
    CLOUD_TOPIC_NUMBER_INDEX,
    DOMAIN,
    LOGGER,
)
from .coordinator import PulsonAlarmDataUpdateCoordinator
from .data import IntegrationPulsonAlarmData
from .mqtt_client import PulsonConfig, PulsonMqttClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import IntegrationPulsonAlarmConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.ALARM_CONTROL_PANEL,
]


async def register_panel(hass: HomeAssistant) -> None:
    """Register cudtom panel of integration."""
    panel_dir = Path(__file__).parent / "www" / "panel"
    assets_dir = panel_dir / "assets"
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig("/pulson_alarm_panel", str(panel_dir), False),
            StaticPathConfig("/pulson_alarm_panel/assets", str(assets_dir), False),
        ]
    )

    # Znajdź plik index-*.js (z hashem)
    try:
        js_file = next(
            f"/pulson_alarm_panel/assets/{p.name}"
            for p in assets_dir.iterdir()
            if p.name.startswith("index-") and p.suffix == ".js"
        )
    except StopIteration as exc:
        msg = "Bundle Reacta nie został znaleziony w katalogu assets"
        raise FileNotFoundError(msg) from exc

    await async_register_panel(
        hass=hass,
        frontend_url_path="pulson-alarm",
        webcomponent_name="pulson-alarm-panel",
        sidebar_title="Pulson Alarm",
        sidebar_icon="mdi:shield-home",
        module_url=js_file,
        require_admin=False,
    )


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationPulsonAlarmConfigEntry,
) -> bool:
    """Set up the debugger."""
    if os.getenv("HA_DEBUG", "0") == "1" and not debugpy.is_client_connected():
        debugpy.listen(("0.0.0.0", 5678))  # noqa: S104 TODO:delete debugger
        debugpy.wait_for_client()
        # debugpy.breakpoint()  # noqa: ERA001

    """Setup MQTT connection."""
    cfg_data = entry.data
    cfg = PulsonConfig(
        host=cfg_data["host"],
        port=int(cfg_data.get("port", 8883)),
        username=cfg_data.get("username", ""),
        password=cfg_data.get("password", ""),
        serial_number=cfg_data.get("serial_number", ""),
        user_code=cfg_data.get("code", ""),
    )
    mqtt_client = PulsonMqttClient(cfg)

    api_client = IntegrationPulsonAlarmApiClient(
        session=async_get_clientsession(hass),
        mqtt_client=mqtt_client,
    )

    """Set up this integration using UI."""
    coordinator = PulsonAlarmDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(hours=1),
        api_client=api_client,
    )

    entry.runtime_data = IntegrationPulsonAlarmData(
        api_client=api_client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "mqtt_client": mqtt_client,
        "coordinator": coordinator,
    }

    api_client.entity_register_update_callback(coordinator.async_update_listeners)

    # MQTT receive handler with api
    async def handle_message(topic: str, payload: str) -> None:
        LOGGER.info("Odebrano z MQTT: %s = %s", topic, payload)
        parts = topic.split("/")
        if (
            len(parts) > CLOUD_TOPIC_MODULE_INDEX
            and parts[CLOUD_TOPIC_MODULE_INDEX] == "inputs"
        ):
            input_id = parts[CLOUD_TOPIC_NUMBER_INDEX]
            key = parts[CLOUD_TOPIC_ACTION_INDEX]
            if payload.__len__ == 0:
                return
            try:
                api_client.input_update_param(input_id, key, payload)
            except (ValueError, TypeError) as e:
                LOGGER.warning("Problem with parsing input state: %s", e)
        elif (
            len(parts) > CLOUD_TOPIC_MODULE_INDEX
            and parts[CLOUD_TOPIC_MODULE_INDEX] == "partitions"
        ):
            partition_id = parts[CLOUD_TOPIC_NUMBER_INDEX]
            key = parts[CLOUD_TOPIC_ACTION_INDEX]
            if payload.__len__ == 0:
                return
            try:
                api_client.partition_update_param(partition_id, key, payload)
            except (ValueError, TypeError) as e:
                LOGGER.warning("Problem with parsing partition state: %s", e)

    # Start MQTT z handlerem
    await mqtt_client.start(handle_message)

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    hass.http.register_view(PulsonLinesView(api_client))
    await register_panel(hass)  # noqa: ERA001
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: IntegrationPulsonAlarmConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    client = hass.data[DOMAIN][entry.entry_id]["mqtt_client"]
    await client.stop()
    hass.components.frontend.async_remove_panel("pulson-alarm")
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: IntegrationPulsonAlarmConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class PulsonLinesView(HomeAssistantView):
    url = "/api/pulson_alarm/lines"
    name = "api:pulson_alarm_lines"
    requires_auth = True

    def __init__(self, api_client):
        self.api_client = api_client

    async def get(self, request):
        data = self.api_client.inputs 
        return self.json(data)
