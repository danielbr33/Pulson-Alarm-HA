"""Define alarm panel entity."""

from collections.abc import Callable

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
)
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pulson_alarm.api import IntegrationPulsonAlarmApiClient
from pulson_alarm.const import DOMAIN
from pulson_alarm.coordinator import PulsonAlarmDataUpdateCoordinator

from .partition_sensor import PartitionState, _safe_int


def create_alarm_panel_adder(
    coordinator: PulsonAlarmDataUpdateCoordinator,
    api: IntegrationPulsonAlarmApiClient,
    async_add_entities: AddEntitiesCallback,
) -> Callable[[str], None]:
    """Create a function that adds alarm panel entities dynamically."""
    registered_panels: dict[str, PulsonAlarmPanel] = {}

    def add_alarm_panel(partition_id: str) -> None:
        if partition_id in registered_panels:
            return

        panel_entity = PulsonAlarmPanel(coordinator, partition_id, api)
        registered_panels[partition_id] = panel_entity

        async_add_entities([panel_entity])

    return add_alarm_panel


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up alarm panel platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: PulsonAlarmDataUpdateCoordinator = data["coordinator"]
    api: IntegrationPulsonAlarmApiClient = coordinator.api_client

    add_alarm_panel = create_alarm_panel_adder(coordinator, api, async_add_entities)
    api.partition_register_added_callback(add_alarm_panel)

    for partition_id in api.partition_get_all_ids():
        add_alarm_panel(partition_id)


class PulsonAlarmPanel(AlarmControlPanelEntity, CoordinatorEntity):
    """Representation of an Alarm Panel (partition) entity."""

    def __init__(
        self,
        coordinator: PulsonAlarmDataUpdateCoordinator,
        partition_id: str,
        api: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize the panel entity."""
        super().__init__(coordinator)
        self._partition_id = partition_id
        self._api = api
        self._attr_unique_id = f"{DOMAIN}_alarm_panel_{partition_id}"
        self._attr_name = f"Partycja {partition_id}"
        self._attr_code_format = "number"  # type: ignore  # noqa: PGH003

        self._attr_supported_features = (
            AlarmControlPanelEntityFeature.ARM_HOME
            | AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.ARM_NIGHT
        )

    @property
    def state(self) -> str:
        """Return the current state."""
        data = self._api.partition_get_state(self._partition_id)
        status = _safe_int(data.get("status"))

        match status:
            case PartitionState.DISARMED:
                return AlarmControlPanelState.DISARMED
            case PartitionState.ARMED:
                return AlarmControlPanelState.ARMED_AWAY
            case PartitionState.ARMED_NIGHT:
                return AlarmControlPanelState.ARMED_NIGHT
            case PartitionState.ENTRY_TIME | PartitionState.ENTRY_TIME_NIGHT:
                return AlarmControlPanelState.PENDING
            case PartitionState.EXIT_TIME | PartitionState.EXIT_TIME_NIGHT:
                return AlarmControlPanelState.ARMING
            case _:
                return AlarmControlPanelState.PENDING

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        await self._api.partition_disarm(self._partition_id, code)
        self.async_write_ha_state()

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm command."""
        await self._api.partition_arm(self._partition_id, code)
        self.async_write_ha_state()

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send 'home' (stay) arm command. Can be same as 'away'."""
        await self._api.partition_arm(self._partition_id, code)
        self.async_write_ha_state()

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send night arm command."""
        await self._api.partition_arm_night(self._partition_id, code)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if partition is ready and active."""
        data = self._api.partition_get_state(self._partition_id)
        return bool(_safe_int(data.get("ready"))) and str(
            data.get("active", "")
        ).lower().startswith("true")

    @property
    def device_info(self) -> dict:
        """Device info to group entities under one device."""
        return {
            "identifiers": {(DOMAIN, f"partition_alarm_panel_{self._partition_id}")},
            "name": f"Partycja {self._partition_id} - Panel alarmowy",
            "manufacturer": "Pulson Alarm",
            "model": "Alarm Panel",
            "entry_type": "service",
        }
