"""Entity of line."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pulson_alarm.const import LOGGER

STATUS_MAP = {
    0: ("Nieznany", "mdi:help-circle"),
    1: ("Zamknięta", "mdi:lock"),
    2: ("Otwarta", "mdi:lock-open"),
    3: ("Sabotaż", "mdi:alert"),
    4: ("Usterka", "mdi:alert-octagon"),
}


class AlarmInputSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, input_id, api):
        super().__init__(coordinator)
        self._input_id = input_id
        self._api = api
        self._attr_unique_id = f"pulson_input_{input_id}"
        self._attr_name = f"Wejście {input_id}"

    @property
    def state(self):
        input_data = self._api.input_get_state(self._input_id)
        status = input_data.get("status")
        LOGGER.debug("Sensor [%s] status: %s", self._input_id, status)
        return STATUS_MAP.get(status, ("Nieznany",))[0]

    @property
    def icon(self):
        input_data = self._api.input_get_state(self._input_id)
        status = input_data.get("status")
        return STATUS_MAP.get(status, ("", "mdi:help-circle"))[1]

    @property
    def extra_state_attributes(self):
        input_data = self._api.input_get_state(self._input_id) or {}
        return {
            "block": bool(input_data.get("block", False)),
            "block_status": bool(input_data.get("block_status", False)),
            "name": input_data.get("name", f"Wejście {self._input_id}"),
        }
