"""The Ambient One Air Quality integration."""
from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AmbientOneAPIError, AmbientOneAuthError, AmbientOneClient
from .const import DOMAIN, PLATFORMS, SCAN_INTERVAL_SECONDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ambient One from a config entry."""
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]

    session = async_get_clientsession(hass)
    client = AmbientOneClient(email, password, session)

    try:
        await client.authenticate()
        devices = await client.get_devices()
    except AmbientOneAuthError as err:
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
    except AmbientOneAPIError as err:
        raise ConfigEntryNotReady(f"Failed to connect to Ambient One API: {err}") from err

    if not devices:
        _LOGGER.warning("No Ambient One devices found for this account")

    async def async_update_data():
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(30):
                devices = await client.get_devices()
                device_data = {}

                for device in devices:
                    # Get full sensor data
                    sensor_data = await client.get_sensor_data(device.device_id, realtime=False)
                    device_data[device.device_id] = {
                        "device": device,
                        "sensor_data": sensor_data,
                    }

                return device_data
        except AmbientOneAuthError as err:
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
        except AmbientOneAPIError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
