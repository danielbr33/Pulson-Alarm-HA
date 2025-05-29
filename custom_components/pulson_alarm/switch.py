"""Main handler of switch entities responsible for adding them and refreshing."""

from collections.abc import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pulson_alarm.partition_sensor import (
    AlarmPartitionArmButton,
    AlarmPartitionArmNightButton,
)

from .api import IntegrationPulsonAlarmApiClient
from .const import DOMAIN
from .coordinator import PulsonAlarmDataUpdateCoordinator
from .line_sensor import AlarmLineBlockSwitch


def create_input_switch_adder(
    coordinator: PulsonAlarmDataUpdateCoordinator,
    api: IntegrationPulsonAlarmApiClient,
    async_add_entities: AddEntitiesCallback,
) -> Callable[[str], None]:
    """Create a function that adds new switch entities for block control dynamically."""
    registered: dict[str, AlarmLineBlockSwitch] = {}

    def add_input_switch(input_id: str) -> None:
        if input_id in registered:
            return

        switch_entity = AlarmLineBlockSwitch(coordinator, input_id, api)
        registered[input_id] = switch_entity
        async_add_entities([switch_entity])

    return add_input_switch


def create_partition_switch_adder(
    coordinator: PulsonAlarmDataUpdateCoordinator,
    api: IntegrationPulsonAlarmApiClient,
    async_add_entities: AddEntitiesCallback,
) -> Callable[[str], None]:
    """Create a function that adds new switch entities of partition."""
    registered: dict[str, list] = {}

    def add_partition_switch(partition_id: str) -> None:
        if partition_id in registered:
            return

        switch_entity = AlarmPartitionArmButton(coordinator, partition_id, api)
        switch__night_entity = AlarmPartitionArmNightButton(
            coordinator, partition_id, api
        )
        registered[partition_id] = [switch_entity, switch__night_entity]
        async_add_entities([switch_entity, switch__night_entity])

    return add_partition_switch


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PulsonAlarmDataUpdateCoordinator = data["coordinator"]
    api: IntegrationPulsonAlarmApiClient = coordinator.api_client

    add_block_switch = create_input_switch_adder(coordinator, api, async_add_entities)
    api.input_register_added_callback(add_block_switch)
    add_partition_switch = create_partition_switch_adder(
        coordinator, api, async_add_entities
    )
    api.partition_register_added_callback(add_partition_switch)

    for input_id in api.input_get_all_ids():
        add_block_switch(input_id)
    for partition_id in api.partition_get_all_ids():
        add_partition_switch(partition_id)
