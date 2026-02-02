"""Constants for the Ambient One integration."""
from homeassistant.const import Platform

DOMAIN = "ambient_one"
PLATFORMS = [Platform.SENSOR, Platform.AIR_QUALITY]

# Configuration keys
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Update intervals
SCAN_INTERVAL_SECONDS = 60  # Poll every 60 seconds

# Device attributes
ATTR_DEVICE_ID = "device_id"
ATTR_FIRMWARE_VERSION = "firmware_version"
ATTR_BATTERY = "battery_percentage"
ATTR_WIFI_RSSI = "wifi_rssi"
ATTR_LAST_SEEN = "last_seen"
ATTR_LOCATION = "location"
ATTR_AQI_CATEGORY = "aqi_category"
ATTR_PRIMARY_POLLUTANT = "primary_pollutant"
