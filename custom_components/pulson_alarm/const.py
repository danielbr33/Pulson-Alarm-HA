"""Constants for pulson_alarm."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "pulson_alarm"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_SERIAL_NUMBER = "serial_number"
CONF_CLOUD_HOST = "host"
CONF_CLOUD_USER = "username"
CONF_CLOUD_PASSWORD = "password"  # noqa: S105
CONF_CLOUD_PORT = "port"

CLOUD_TOPIC_SYSTEM_INDEX = 0
CLOUD_TOPIC_SYSTEMID_INDEX = 1
CLOUD_TOPIC_MODULE_INDEX = 2
CLOUD_TOPIC_NUMBER_INDEX = 3
CLOUD_TOPIC_ACTION_INDEX = 4
CLOUD_TOPIC_SUBTYPE_INDEX = 5
