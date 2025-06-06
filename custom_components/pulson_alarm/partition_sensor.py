"""
Entities for representing alarm partition in Home Assistant.

Includes:
- Sensor entity for partition status (PARTITION_STATUS_MAP).
- Switch entity for arming/disarming
"""

from enum import IntEnum

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pulson_alarm.api import IntegrationPulsonAlarmApiClient
from pulson_alarm.const import DOMAIN
from pulson_alarm.coordinator import PulsonAlarmDataUpdateCoordinator


class PartitionStatusInfo:
    """Class with description and icon for partition status."""

    def __init__(self, description: str, icon: str) -> None:
        """Set description and icon."""
        self.description = description
        self.icon = icon

    def __repr__(self) -> str:
        """Return partition info in string."""
        return f"PartitionStatusInfo(desc='{self.description}', icon='{self.icon}')"


class PartitionState(IntEnum):
    """Enumaration of partition states."""

    DISARMED = 0
    ARMED = 1
    ARMED_NIGHT = 2
    ENTRY_TIME = 3
    EXIT_TIME = 4
    ALARM_INTRUDER = 5
    ALARM_FIRE = 6
    ALARM_GAS = 7
    ALARM_CO = 8
    ALARM_MEDICAL = 9
    ALARM_DEFINED = 10
    ALARM_SABOTAGE_TAMPER = 11
    ALARM_FLOOD = 12
    ALARM_TEMPERATURE = 13
    ENTRY_TIME_NIGHT = 14
    EXIT_TIME_NIGHT = 15
    ALARM_PANIC = 16
    ALARM_HOLDUP = 17
    ALARM_SABOTAGE_ZONE = 18
    ALARM_IN_MEMORY = 19
    UNKNOWN = -1


PartitionStatusMap: dict[PartitionState, PartitionStatusInfo] = {
    PartitionState.DISARMED: PartitionStatusInfo("Rozbrojony", "mdi:shield-off"),
    PartitionState.ARMED: PartitionStatusInfo("Uzbrojony", "mdi:shield-check"),
    PartitionState.ARMED_NIGHT: PartitionStatusInfo(
        "Uzbrojony noc", "mdi:weather-night"
    ),
    PartitionState.ENTRY_TIME: PartitionStatusInfo("Czas wejścia", "mdi:run"),
    PartitionState.EXIT_TIME: PartitionStatusInfo("Czas wyjścia", "mdi:exit-run"),
    PartitionState.ALARM_INTRUDER: PartitionStatusInfo(
        "Alarm włamaniowy", "mdi:alarm-light"
    ),
    PartitionState.ALARM_FIRE: PartitionStatusInfo("Alarm pożarowy", "mdi:fire-alert"),
    PartitionState.ALARM_GAS: PartitionStatusInfo("Alarm gazowy", "mdi:gas-cylinder"),
    PartitionState.ALARM_CO: PartitionStatusInfo("Alarm czadu", "mdi:molecule-co"),
    PartitionState.ALARM_MEDICAL: PartitionStatusInfo(
        "Alarm medyczny", "mdi:medical-bag"
    ),
    PartitionState.ALARM_DEFINED: PartitionStatusInfo(
        "Alarm zdefiniowany", "mdi:alert-decagram"
    ),
    PartitionState.ALARM_SABOTAGE_TAMPER: PartitionStatusInfo(
        "Sabotaż / manipulacja", "mdi:alert"
    ),
    PartitionState.ALARM_FLOOD: PartitionStatusInfo("Alarm zalania", "mdi:water"),
    PartitionState.ALARM_TEMPERATURE: PartitionStatusInfo(
        "Alarm temperatury", "mdi:thermometer-alert"
    ),
    PartitionState.ENTRY_TIME_NIGHT: PartitionStatusInfo(
        "Czas wejścia (noc)", "mdi:run"
    ),
    PartitionState.EXIT_TIME_NIGHT: PartitionStatusInfo(
        "Czas wyjścia (noc)", "mdi:exit-run"
    ),
    PartitionState.ALARM_PANIC: PartitionStatusInfo(
        "Alarm paniki", "mdi:alert-octagon"
    ),
    PartitionState.ALARM_HOLDUP: PartitionStatusInfo("Alarm napadowy", "mdi:handcuffs"),
    PartitionState.ALARM_SABOTAGE_ZONE: PartitionStatusInfo(
        "Sabotaż strefy", "mdi:security"
    ),
    PartitionState.ALARM_IN_MEMORY: PartitionStatusInfo(
        "Alarm w pamięci", "mdi:history"
    ),
    PartitionState.UNKNOWN: PartitionStatusInfo("Nieznany", "mdi:help-circle"),
}


def _safe_int(value: str | int | None) -> int:
    """
    Safely convert a value to int, or return default if conversion fails.

    Handles None, invalid strings, and type errors.
    """
    if value is None:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


class AlarmPartitionSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity representing the status of an alarm partition."""

    def __init__(
        self,
        coordinator: PulsonAlarmDataUpdateCoordinator,
        partition_id: str,
        api: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize Alarm Line entity."""
        super().__init__(coordinator)
        self._partition_id = partition_id
        self._api = api
        self._attr_unique_id = f"pulson_partition_status_{partition_id}"
        self._attr_name = f"Partycja {partition_id} - Stan"

    @property
    def state(self) -> str:
        """Return the current status label for the partition."""
        data = self._api.partition_get_state(self._partition_id)
        status = _safe_int(data.get("status"))
        try:
            state_enum = PartitionState(status)
            return PartitionStatusMap[state_enum].description
        except (ValueError, KeyError):
            return PartitionStatusMap[PartitionState.UNKNOWN].description

    @property
    def icon(self) -> str:
        """Return an appropriate icon based on the partition's status."""
        data = self._api.partition_get_state(self._partition_id)
        status = _safe_int(data.get("status"))
        try:
            state_enum = PartitionState(status)
            return PartitionStatusMap[state_enum].icon
        except (ValueError, KeyError):
            return PartitionStatusMap[PartitionState.UNKNOWN].icon

    @property
    def extra_state_attributes(self) -> dict:
        """Provide basic device metadata for Home Assistant device registry."""
        data = self._api.partition_get_state(self._partition_id)
        return {
            "exit_time": _safe_int(data.get("exit_time")),
            "ready": _safe_int(data.get("ready")),
            "night_mode": bool(_safe_int(data.get("night_mode"))),
            "active": bool(_safe_int(data.get("active"))),
        }

    @property
    def device_info(self) -> dict:
        """Provide basic device metadata for Home Assistant device registry."""
        return {
            "identifiers": {(DOMAIN, f"partition_{self._partition_id}")},
            "name": f"Partycja {self._partition_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Partycja",
            "entry_type": "service",
        }


class AlarmPartitionArmButton(CoordinatorEntity, SwitchEntity):
    """
    Switch entity for enabling arming or disarming partition.

    The switch is 'on' when the partition is ready to arm.
    """

    def __init__(
        self,
        coordinator: PulsonAlarmDataUpdateCoordinator,
        partition_id: str,
        api: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize Alarm Partition entity."""
        super().__init__(coordinator)
        self._partition_id = partition_id
        self._api = api
        self._attr_unique_id = f"pulson_partition_arm_button_{partition_id}"
        self._attr_name = f"Partycja {partition_id} - Uzbrojenie"
        self._attr_icon = "mdi:shield-lock"

    @property
    def is_on(self) -> bool:
        """Return True if partition is armed."""
        data = self._api.partition_get_state(self._partition_id)
        return _safe_int(data.get("status")) != PartitionState.DISARMED

    @property
    def available(self) -> bool:
        """Return True if the partition can be armed."""
        data = self._api.partition_get_state(self._partition_id)
        return bool(_safe_int(data.get("ready")))

    async def async_turn_on(self) -> None:
        """Send command to arm partition."""
        await self._api.partition_arm(self._partition_id)
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Send command to disarm partition."""
        await self._api.partition_disarm(self._partition_id)
        self.async_write_ha_state()

    @property
    def device_info(self) -> dict:
        """Provide basic device metadata for Home Assistant device registry."""
        return {
            "identifiers": {(DOMAIN, f"partition_{self._partition_id}")},
            "name": f"Partycja {self._partition_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Przycisk uzbrojenia",
            "entry_type": "service",
        }


class AlarmPartitionArmNightButton(CoordinatorEntity, SwitchEntity):
    """
    Switch entity for enabling night arming or disarming partition.

    The switch is 'on' when the partition is ready to arm.
    """

    def __init__(
        self,
        coordinator: PulsonAlarmDataUpdateCoordinator,
        partition_id: str,
        api: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize Alarm Partition entity."""
        super().__init__(coordinator)
        self._partition_id = partition_id
        self._api = api
        self._attr_unique_id = f"pulson_partition_arm_night_button_{partition_id}"
        self._attr_name = f"Partycja {partition_id} - Uzbrojenie nocne"
        self._attr_icon = "mdi:shield-home"

    @property
    def is_on(self) -> bool:
        """Return True if partition is armed."""
        data = self._api.partition_get_state(self._partition_id)
        return bool(_safe_int(data.get("status")) == PartitionState.ARMED_NIGHT)

    @property
    def available(self) -> bool:
        """Return True if the partition can be armed."""
        data = self._api.partition_get_state(self._partition_id)
        return bool(_safe_int(data.get("ready"))) and data.get("night_mode") == "true"

    async def async_turn_on(self) -> None:
        """Send command to arm partition."""
        await self._api.partition_arm_night(self._partition_id)
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Send command to disarm partition."""
        await self._api.partition_disarm(self._partition_id)
        self.async_write_ha_state()

    @property
    def device_info(self) -> dict:
        """Provide basic device metadata for Home Assistant device registry."""
        return {
            "identifiers": {(DOMAIN, f"partition_{self._partition_id}")},
            "name": f"Partycja {self._partition_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Przycisk uzbrojenia nocnego",
            "entry_type": "service",
        }
