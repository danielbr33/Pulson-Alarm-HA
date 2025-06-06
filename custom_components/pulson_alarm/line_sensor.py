"""
Entities for representing alarm input lines in Home Assistant.

Includes:
- Sensor entity for input line status (open, closed, tamper, fault).
- Switch entity for enabling/disabling line blocking.
"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pulson_alarm.api import IntegrationPulsonAlarmApiClient
from pulson_alarm.const import DOMAIN
from pulson_alarm.coordinator import PulsonAlarmDataUpdateCoordinator

STATUS_MAP = {
    0: ("Nieznany", "mdi:help-circle"),
    1: ("Zamknięta", "mdi:lock"),
    2: ("Otwarta", "mdi:lock-open"),
    3: ("Sabotaż", "mdi:alert"),
    4: ("Usterka", "mdi:alert-octagon"),
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


class AlarmLineStatusSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity representing the status of an alarm input line.

    The state is derived from the API's 'status' value (e.g. open, closed, tamper).
    """

    def __init__(
        self,
        coordinator: PulsonAlarmDataUpdateCoordinator,
        input_id: str,
        api: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize Alarm Line entity."""
        super().__init__(coordinator)
        self._input_id = input_id
        self._api = api
        self._attr_unique_id = f"pulson_line_status_{input_id}"
        self._attr_name = f"Linia {input_id} - Stan"

    @property
    def state(self) -> str:
        """Return the current status label for the line."""
        data = self._api.input_get_state(self._input_id)
        status = _safe_int(data.get("status"))
        return STATUS_MAP.get(status, ("Nieznany",))[0]

    @property
    def icon(self) -> str:
        """Return an appropriate icon based on the line's status."""
        data = self._api.input_get_state(self._input_id)
        status = _safe_int(data.get("status"))
        return STATUS_MAP.get(status, ("", "mdi:help-circle"))[1]

    @property
    def device_info(self) -> dict:
        """Provide basic device metadata for Home Assistant device registry."""
        return {
            "identifiers": {(DOMAIN, f"line_{self._input_id}")},
            "name": f"Linia {self._input_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Wejście alarmowe",
            "entry_type": "service",
        }


class AlarmLineBlockSwitch(CoordinatorEntity, SwitchEntity):
    """
    Switch entity for enabling or disabling the blocking of an alarm line.

    The switch is 'on' when the line is currently blocked.
    It is available only when 'block_enable' is True in the API state.
    """

    def __init__(
        self,
        coordinator: PulsonAlarmDataUpdateCoordinator,
        input_id: str,
        api: IntegrationPulsonAlarmApiClient,
    ) -> None:
        """Initialize Alarm Line Blockade entity."""
        super().__init__(coordinator)
        self._input_id = input_id
        self._api = api
        self._attr_unique_id = f"pulson_line_block_{input_id}"
        self._attr_name = f"Linia {input_id} - Blokada"
        self._attr_icon = "mdi:block-helper"

    @property
    def is_on(self) -> bool:
        """Return True if the line is currently blocked."""
        data = self._api.input_get_state(self._input_id)
        return bool(_safe_int(data.get("block")))

    @property
    def available(self) -> bool:
        """Return True if the line can be blocked."""
        data = self._api.input_get_state(self._input_id)
        return bool(_safe_int(data.get("block_enable")))

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes, such as whether blocking is allowed."""
        data = self._api.input_get_state(self._input_id)
        return {"blokada_dostępna": bool(_safe_int(data.get("block_enable")))}

    async def async_turn_on(self) -> None:
        """Send command to enable blocking for this line."""
        await self._api.set_input_block_state(self._input_id, block=True)
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Send command to disable blocking for this line."""
        await self._api.set_input_block_state(self._input_id, block=False)
        self.async_write_ha_state()

    @property
    def device_info(self) -> dict:
        """Provide basic device metadata for Home Assistant device registry."""
        return {
            "identifiers": {(DOMAIN, f"line_{self._input_id}")},
            "name": f"Linia {self._input_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Wejście alarmowe",
            "entry_type": "service",
        }
