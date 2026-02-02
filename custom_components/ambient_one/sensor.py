"""Sensor platform for Ambient One."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AmbientOneDevice, AmbientOneSensorData
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class AmbientOneSensorEntityDescription(SensorEntityDescription):
    """Describes Ambient One sensor entity."""

    value_fn: Callable[[AmbientOneSensorData], float | int | str | None] | None = None


SENSOR_TYPES: tuple[AmbientOneSensorEntityDescription, ...] = (
    AmbientOneSensorEntityDescription(
        key="pm2_5",
        name="PM2.5",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.pm2_5,
    ),
    AmbientOneSensorEntityDescription(
        key="pm1_0",
        name="PM1.0",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM1,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.pm1_0,
    ),
    AmbientOneSensorEntityDescription(
        key="pm4_0",
        name="PM4.0",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.pm4_0,
    ),
    AmbientOneSensorEntityDescription(
        key="pm10_0",
        name="PM10",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.pm10_0,
    ),
    AmbientOneSensorEntityDescription(
        key="co2",
        name="CO2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.co2,
    ),
    AmbientOneSensorEntityDescription(
        key="voc_index",
        name="VOC Index",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chemical-weapon",
        value_fn=lambda data: data.voc_index,
    ),
    AmbientOneSensorEntityDescription(
        key="nox_index",
        name="NOx Index",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:smog",
        value_fn=lambda data: data.nox_index,
    ),
    AmbientOneSensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.temperature,
    ),
    AmbientOneSensorEntityDescription(
        key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.humidity,
    ),
    AmbientOneSensorEntityDescription(
        key="iaq_score",
        name="Indoor Air Quality Score",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        value_fn=lambda data: data.iaq_score,
    ),
    AmbientOneSensorEntityDescription(
        key="aqi_category",
        name="Air Quality Category",
        icon="mdi:information-outline",
        value_fn=lambda data: data.aqi_category,
    ),
    AmbientOneSensorEntityDescription(
        key="battery",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=None,  # Special handling needed
    ),
    AmbientOneSensorEntityDescription(
        key="wifi_signal",
        name="WiFi Signal",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=None,  # Special handling needed
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ambient One sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[AmbientOneSensor] = []

    for device_id, device_data in coordinator.data.items():
        device = device_data["device"]

        for description in SENSOR_TYPES:
            entities.append(
                AmbientOneSensor(
                    coordinator,
                    device,
                    description,
                )
            )

    async_add_entities(entities)


class AmbientOneSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Ambient One sensor."""

    entity_description: AmbientOneSensorEntityDescription

    def __init__(
        self,
        coordinator,
        device: AmbientOneDevice,
        description: AmbientOneSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device = device

        # Entity IDs and unique IDs
        self._attr_unique_id = f"{device.device_id}_{description.key}"
        self._attr_name = f"{device.name} {description.name}"

        # Device info for grouping entities
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.device_id)},
            "name": device.name,
            "manufacturer": "Ambient Works",
            "model": "Ambient One",
            "sw_version": device.firmware_version,
        }

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        device_data = self.coordinator.data.get(self._device.device_id)
        if not device_data:
            return None

        # Special handling for device attributes (not sensor data)
        if self.entity_description.key == "battery":
            return device_data["device"].battery_percentage
        elif self.entity_description.key == "wifi_signal":
            return device_data["device"].wifi_rssi

        # Get sensor data
        sensor_data = device_data.get("sensor_data")
        if not sensor_data or not self.entity_description.value_fn:
            return None

        return self.entity_description.value_fn(sensor_data)

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
            "last_seen": device.last_seen,
        }

        if device.location_name:
            attributes["location"] = device.location_name

        # Add air quality context for relevant sensors
        if sensor_data and self.entity_description.key in [
            "pm2_5",
            "pm1_0",
            "pm4_0",
            "pm10_0",
            "co2",
            "voc_index",
            "nox_index",
        ]:
            if sensor_data.aqi_category:
                attributes["aqi_category"] = sensor_data.aqi_category
            if sensor_data.primary_pollutant:
                attributes["primary_pollutant"] = sensor_data.primary_pollutant

        return attributes
