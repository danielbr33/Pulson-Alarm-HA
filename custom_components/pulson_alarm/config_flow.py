#!/usr/local/bin python
"""Adds config flow for PulsonAlarm."""

from __future__ import annotations

import json
from pathlib import Path

import voluptuous as vol
from asyncio_mqtt import MqttError
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from pulson_alarm.mqtt_client import PulsonMqttClient

from .api import (
    IntegrationPulsonAlarmApiClient,
    IntegrationPulsonAlarmApiClientAuthenticationError,
    IntegrationPulsonAlarmApiClientCommunicationError,
    IntegrationPulsonAlarmApiClientError,
)
from .const import (
    CONF_CLOUD_HOST,
    CONF_CLOUD_PASSWORD,
    CONF_CLOUD_PORT,
    CONF_CLOUD_USER,
    CONF_SERIAL_NUMBER,
    DOMAIN,
    LOGGER,
)


class PulsonAlarmFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for PulsonAlarm."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        # Wczytaj domyślne wartości z JSON
        default_values = {}
        try:
            file_path = Path(__file__).parent / "default_log.json"
            with file_path.open("r", encoding="utf-8") as f:
                default_values = json.load(f)
        except FileNotFoundError:
            LOGGER.warning("File default_log.json does not exist.")
        except json.JSONDecodeError as e:
            LOGGER.error("JSON decode error in default_log.json: %s", e)
        except OSError as e:
            LOGGER.error("I/O error reading default_log.json: %s", e)

        # Jeżeli użytkownik wysłał dane
        if user_input is not None:
            try:
                await self._test_credentials(
                    mqtt_host=user_input[CONF_CLOUD_HOST],
                    mqtt_port=user_input[CONF_CLOUD_PORT],
                    mqtt_username=user_input[CONF_CLOUD_USER],
                    mqtt_password=user_input[CONF_CLOUD_PASSWORD],
                )
            except IntegrationPulsonAlarmApiClientAuthenticationError:
                _errors["base"] = "auth"
            except IntegrationPulsonAlarmApiClientCommunicationError:
                _errors["base"] = "connection"
            except IntegrationPulsonAlarmApiClientError:
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(slugify(user_input[CONF_CLOUD_USER]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_CLOUD_USER],
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_CLOUD_HOST,
                    default=default_values.get(CONF_CLOUD_HOST, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(
                    CONF_SERIAL_NUMBER,
                    default=default_values.get(CONF_SERIAL_NUMBER, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_CLOUD_PORT,
                    default=int(default_values.get(CONF_CLOUD_PORT, 8883)),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1,
                        max=65535,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(
                    CONF_CLOUD_USER,
                    default=default_values.get(CONF_CLOUD_USER, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional(
                    CONF_CLOUD_PASSWORD,
                    default=default_values.get(CONF_CLOUD_PASSWORD, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=_errors,
        )

    async def _test_credentials(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_username: str,
        mqtt_password: str,
    ) -> None:
        """Test if provided credentials allow access to the API and MQTT."""
        mqtt_client = PulsonMqttClient(
            host=mqtt_host,
            port=int(mqtt_port),
            username=mqtt_username,
            password=mqtt_password,
            serial_number="",
        )

        try:
            try:
                await mqtt_client.start(None)
            except MqttError as e:
                msg = "MQTT test failed"
                raise MqttError(msg) from e
            api_client = IntegrationPulsonAlarmApiClient(
                session=async_create_clientsession(self.hass),
                mqtt_client=mqtt_client,
            )
            await api_client.async_get_data()

        finally:
            LOGGER.info("Form data correct, credentials accepted and tested")
            await mqtt_client.stop()
