"""Air Quality platform for Ambient One."""
from __future__ import annotations

import logging

from homeassistant.components.air_quality import AirQualityEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AmbientOneDevice
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambient One air quality from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[AmbientOneAirQuality] = []

    for device_id, device_data in coordinator.data.items():
        device = device_data["device"]
        entities.append(AmbientOneAirQuality(coordinator, device))

    async_add_entities(entities)


class AmbientOneAirQuality(CoordinatorEntity, AirQualityEntity):
    """Representation of an Ambient One Air Quality entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device: AmbientOneDevice) -> None:
        """Initialize the air quality entity."""
        super().__init__(coordinator)
        self._device = device

        # Entity IDs and unique IDs
        self._attr_unique_id = f"{device.device_id}_air_quality"
        self._attr_name = "Air Quality"

        # Device info for grouping entities
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Ambient Works",
            "model": "Ambient One",
            "sw_version": device.firmware_version,
        }

    @property
    def air_quality_index(self) -> float | None:
        """Return the Air Quality Index (AQI)."""
        device_data = self.coordinator.data.get(self._device.device_id)
        if not device_data:
            return None

        sensor_data = device_data.get("sensor_data")
        if not sensor_data:
            return None

        # Use IAQ score as the primary index
        # Scale from 0-10 to 0-500 for better visibility
        if sensor_data.iaq_score is not None:
            return round(sensor_data.iaq_score * 50, 1)

        return None

    @property
    def particulate_matter_2_5(self) -> float | None:
        """Return the particulate matter 2.5 level."""
        device_data = self.coordinator.data.get(self._device.device_id)
        if not device_data:
            return None

        sensor_data = device_data.get("sensor_data")
        if sensor_data:
            return sensor_data.pm2_5

        return None

    @property
    def particulate_matter_10(self) -> float | None:
        """Return the particulate matter 10 level."""
        device_data = self.coordinator.data.get(self._device.device_id)
        if not device_data:
            return None

        sensor_data = device_data.get("sensor_data")
        if sensor_data:
            return sensor_data.pm10_0

        return None

    @property
    def carbon_dioxide(self) -> float | None:
        """Return the CO2 (carbon dioxide) level."""
        device_data = self.coordinator.data.get(self._device.device_id)
        if not device_data:
            return None

        sensor_data = device_data.get("sensor_data")
        if sensor_data:
            return sensor_data.co2

        return None

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return "Data provided by Ambient Works"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional attributes."""
        device_data = self.coordinator.data.get(self._device.device_id)
        if not device_data:
            return {}

        device = device_data["device"]
        sensor_data = device_data.get("sensor_data")

        attributes = {
            "device_id": device.device_id,
            "firmware_version": device.firmware_version,
        }

        if device.location_name:
            attributes["location"] = device.location_name

        if sensor_data:
            # Add all available pollutant data
            if sensor_data.pm1_0 is not None:
                attributes["pm1_0"] = sensor_data.pm1_0
            if sensor_data.pm4_0 is not None:
                attributes["pm4_0"] = sensor_data.pm4_0
            if sensor_data.voc_index is not None:
                attributes["voc_index"] = sensor_data.voc_index
            if sensor_data.nox_index is not None:
                attributes["nox_index"] = sensor_data.nox_index
            if sensor_data.temperature is not None:
                attributes["temperature"] = sensor_data.temperature
            if sensor_data.humidity is not None:
                attributes["humidity"] = sensor_data.humidity
            if sensor_data.iaq_score is not None:
                attributes["iaq_score"] = sensor_data.iaq_score
            if sensor_data.aqi_category is not None:
                attributes["aqi_category"] = sensor_data.aqi_category
            if sensor_data.primary_pollutant is not None:
                attributes["primary_pollutant"] = sensor_data.primary_pollutant

        return attributes
