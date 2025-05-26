from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import IntegrationPulsonAlarmApiClient
from .const import DOMAIN
from .coordinator import PulsonAlarmDataUpdateCoordinator
from .line_sensor import AlarmLineBlockSwitch


def create_block_switch_adder(
    coordinator: PulsonAlarmDataUpdateCoordinator,
    api: IntegrationPulsonAlarmApiClient,
    async_add_entities: AddEntitiesCallback,
) -> Callable[[str], None]:
    """Create a function that adds new switch entities for block control dynamically."""
    registered: dict[str, AlarmLineBlockSwitch] = {}

    def add_block_switch(input_id: str) -> None:
        if input_id in registered:
            return

        switch_entity = AlarmLineBlockSwitch(coordinator, input_id, api)
        registered[input_id] = switch_entity
        async_add_entities([switch_entity])

    return add_block_switch


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PulsonAlarmDataUpdateCoordinator = data["coordinator"]
    api: IntegrationPulsonAlarmApiClient = coordinator.api_client

    add_block_switch = create_block_switch_adder(coordinator, api, async_add_entities)
    api.input_register_added_callback(add_block_switch)

    for input_id in api.input_get_all_ids():
        add_block_switch(input_id)
