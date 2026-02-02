"""Config flow for Ambient One integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AmbientOneAPIError, AmbientOneAuthError, AmbientOneClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class AmbientOneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ambient One."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            session = async_get_clientsession(self.hass)
            client = AmbientOneClient(email, password, session)

            try:
                # Try to authenticate
                await client.authenticate()

                # Try to get devices to verify the account works
                devices = await client.get_devices()

                # Create unique ID based on user email
                await self.async_set_unique_id(email.lower())
                self._abort_if_unique_id_configured()

                # Create the config entry
                return self.async_create_entry(
                    title=f"Ambient One ({email})",
                    data=user_input,
                )

            except AmbientOneAuthError:
                errors["base"] = "invalid_auth"
            except AmbientOneAPIError as err:
                _LOGGER.error("Error connecting to Ambient One API: %s", err)
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
