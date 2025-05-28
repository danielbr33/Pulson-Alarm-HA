"""Main handler of sensor entities responsible for adding them and refreshing."""

from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import IntegrationPulsonAlarmApiClient
from .const import DOMAIN
from .coordinator import PulsonAlarmDataUpdateCoordinator
from .line_sensor import (
    AlarmLineStatusSensor,
)


def create_input_entity_adder(
    coordinator: PulsonAlarmDataUpdateCoordinator,
    api: IntegrationPulsonAlarmApiClient,
    async_add_entities: AddEntitiesCallback,
) -> Callable[[str], None]:
    """Create a function that adds new input entities dynamically."""
    registered_status: dict[str, AlarmLineStatusSensor] = {}

    def add_input_entity(input_id: str) -> None:
        if input_id in registered_status:
            return  # already added

        status_entity = AlarmLineStatusSensor(coordinator, input_id, api)

        registered_status[input_id] = status_entity

        async_add_entities([status_entity])

    return add_input_entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PulsonAlarmDataUpdateCoordinator = data["coordinator"]
    api: IntegrationPulsonAlarmApiClient = coordinator.api_client

    # Register callback for dynamic entity creation
    add_input_entity = create_input_entity_adder(coordinator, api, async_add_entities)
    api.input_register_added_callback(add_input_entity)

    # Add already known inputs
    for input_id in api.input_get_all_ids():
        add_input_entity(input_id)
