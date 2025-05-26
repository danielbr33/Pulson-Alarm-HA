from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .line_sensor import AlarmInputSensor

REGISTERED_SENSORS: dict[str, AlarmInputSensor] = {}
ENTITY_ADDER: AddEntitiesCallback | None = None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = coordinator.api_client

    entities = [AlarmInputSensor(coordinator, input_id, api) for input_id in api.inputs]

    async_add_entities(entities)
