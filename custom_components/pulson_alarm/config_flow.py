#!/usr/local/bin python
"""Adds config flow for PulsonAlarm."""

from __future__ import annotations

import json
from pathlib import Path

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .api import (
    IntegrationPulsonAlarmApiClient,
    IntegrationPulsonAlarmApiClientAuthenticationError,
    IntegrationPulsonAlarmApiClientCommunicationError,
    IntegrationPulsonAlarmApiClientError,
)
from .const import DOMAIN, LOGGER


class PulsonAlarmFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for PulsonAlarm."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        default_values = {}
        try:
            file_path = Path(__file__).parent / "default_log.json"
            with file_path.open("r", encoding="utf-8") as f:
                default_values = json.load(f)
        except FileNotFoundError:
            LOGGER.warning("default_config.json nie istnieje.")
        except json.JSONDecodeError as e:
            LOGGER.error("Błąd JSON w default_config.json: %s", e)
        except OSError as e:
            LOGGER.error("Błąd I/O przy próbie wczytania default_config.json: %s", e)

        if user_input is not None:
            try:
                await self._test_credentials(
                    host=user_input["host"],
                    port=user_input["port"],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except IntegrationPulsonAlarmApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationPulsonAlarmApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationPulsonAlarmApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_USERNAME])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "host", default=default_values.get("host", "")
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Required(
                        "serial_number",
                        default=default_values.get("serial_number", ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        "port", default_values.get("port", 1883)
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Optional(
                        CONF_USERNAME, default=default_values.get(CONF_USERNAME, "")
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                    vol.Optional(
                        CONF_PASSWORD, default=default_values.get(CONF_PASSWORD, "")
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                }
            ),
            errors=_errors,
        )

    async def _test_credentials(
        self, host: str, port: int, username: str, password: str
    ) -> None:
        client = IntegrationPulsonAlarmApiClient(
            host=host,
            port=port,
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.async_get_data()
