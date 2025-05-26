from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pulson_alarm.const import DOMAIN, LOGGER

STATUS_MAP = {
    0: ("Nieznany", "mdi:help-circle"),
    1: ("Zamknięta", "mdi:lock"),
    2: ("Otwarta", "mdi:lock-open"),
    3: ("Sabotaż", "mdi:alert"),
    4: ("Usterka", "mdi:alert-octagon"),
}


def _safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


class AlarmLineStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor encja: stan linii (status)."""

    def __init__(self, coordinator, input_id, api):
        super().__init__(coordinator)
        self._input_id = input_id
        self._api = api
        self._attr_unique_id = f"pulson_line_status_{input_id}"
        self._attr_name = f"Linia {input_id} – Stan"

    @property
    def state(self):
        data = self._api.input_get_state(self._input_id)
        status = _safe_int(data.get("status"))
        return STATUS_MAP.get(status, ("Nieznany",))[0]

    @property
    def icon(self):
        data = self._api.input_get_state(self._input_id)
        status = _safe_int(data.get("status"))
        return STATUS_MAP.get(status, ("", "mdi:help-circle"))[1]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"line_{self._input_id}")},
            "name": f"Linia {self._input_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Wejście alarmowe",
            "entry_type": "service",
        }


class AlarmLineBlockEnableSensor(CoordinatorEntity, SensorEntity):
    """Sensor encja: czy linia może być blokowana."""

    def __init__(self, coordinator, input_id, api):
        super().__init__(coordinator)
        self._input_id = input_id
        self._api = api
        self._attr_unique_id = f"pulson_line_block_enable_{input_id}"
        self._attr_name = f"Linia {input_id} – Blokada dostępna"

    @property
    def state(self):
        data = self._api.input_get_state(self._input_id)
        return "Tak" if _safe_int(data.get("block_enable")) else "Nie"

    @property
    def icon(self):
        data = self._api.input_get_state(self._input_id)
        return (
            "mdi:shield-check"
            if _safe_int(data.get("block_enable"))
            else "mdi:shield-off"
        )

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"line_{self._input_id}")},
            "name": f"Linia {self._input_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Wejście alarmowe",
            "entry_type": "service",  # lub "device" – opcjonalne
        }


class AlarmLineBlockSwitch(CoordinatorEntity, SwitchEntity):
    """Switch encja: przełączanie stanu blokady linii."""

    def __init__(self, coordinator, input_id, api):
        super().__init__(coordinator)
        self._input_id = input_id
        self._api = api
        self._attr_unique_id = f"pulson_line_block_{input_id}"
        self._attr_name = f"Linia {input_id} – Blokada"

    @property
    def is_on(self) -> bool:
        data = self._api.input_get_state(self._input_id)
        return bool(_safe_int(data.get("block")))

    @property
    def available(self) -> bool:
        data = self._api.input_get_state(self._input_id)
        return bool(_safe_int(data.get("block_enable")))

    async def async_turn_on(self, **kwargs):
        await self._api.set_input_block_state(self._input_id, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._api.set_input_block_state(self._input_id, False)
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, f"line_{self._input_id}")},
            "name": f"Linia {self._input_id}",
            "manufacturer": "Pulson Alarm",
            "model": "Wejście alarmowe",
            "entry_type": "service",  # lub "device" – opcjonalne
        }
