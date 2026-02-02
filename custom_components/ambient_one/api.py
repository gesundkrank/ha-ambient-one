"""Ambient One API client."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class AmbientOneAPIError(Exception):
    """Base exception for Ambient One API errors."""


class AmbientOneAuthError(AmbientOneAPIError):
    """Authentication error."""


class AmbientOneDevice:
    """Represents an Ambient One device."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize device."""
        self.device_id: str = data["device_id"]
        self.name: str = data["name"]
        self.firmware_version: str | None = data.get("firmware_version")
        self.battery_percentage: int | None = data.get("battery_percentage")
        self.wifi_rssi: int | None = data.get("wifi_rssi")
        self.last_seen: str | None = data.get("last_seen")
        self.location_name: str | None = None
        if data.get("locations"):
            self.location_name = data["locations"].get("name")

    def __repr__(self) -> str:
        """Return representation."""
        return f"<AmbientOneDevice {self.name} ({self.device_id})>"


class AmbientOneSensorData:
    """Represents sensor readings from an Ambient One device."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize sensor data."""
        self.timestamp: str = data.get("timestamp")
        self.pm1_0: float | None = data.get("pm1_0")
        self.pm2_5: float | None = data.get("pm2_5")
        self.pm4_0: float | None = data.get("pm4_0")
        self.pm10_0: float | None = data.get("pm10_0")
        self.temperature: float | None = data.get("temperature")
        self.humidity: float | None = data.get("humidity")
        self.co2: int | None = data.get("co2")
        self.voc_index: int | None = data.get("voc_index")
        self.nox_index: int | None = data.get("nox_index")
        self.iaq_score: float | None = data.get("iaq_score")
        self.aqi_category: str | None = data.get("aqi_category")
        self.primary_pollutant: str | None = data.get("primary_pollutant")


class AmbientOneClient:
    """Client for interacting with the Ambient One API via Supabase."""

    def __init__(
        self,
        email: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the API client."""
        self.email = email
        self.password = password
        self._session = session
        self._own_session = session is None
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expires_at: datetime | None = None
        self._user_id: str | None = None

        # Supabase configuration
        self.base_url = "https://cszlzkwrpugdncexjkbd.supabase.co"
        self.anon_key = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNzemx6a3dycHVnZG5jZXhqa2JkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4MzM1ODYsImV4cCI6MjA2MDQwOTU4Nn0."
            "8hurRr4Pk_oc4utH4Nce8B8GHTgU6m3VaBtTobRDGXs"
        )

    async def __aenter__(self) -> AmbientOneClient:
        """Async context manager entry."""
        if self._own_session:
            self._session = aiohttp.ClientSession()
        await self.authenticate()
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        if self._own_session and self._session:
            await self._session.close()

    def _get_headers(self, use_auth: bool = True) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "apikey": self.anon_key,
            "Content-Type": "application/json",
        }
        if use_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    async def _ensure_token_valid(self) -> None:
        """Ensure the access token is valid, refresh if needed."""
        if not self._access_token:
            await self.authenticate()
            return

        if self._token_expires_at and datetime.now() >= self._token_expires_at - timedelta(minutes=5):
            await self._refresh_access_token()

    async def _refresh_access_token(self) -> None:
        """Refresh the access token using the refresh token."""
        if not self._refresh_token:
            await self.authenticate()
            return

        url = f"{self.base_url}/auth/v1/token?grant_type=refresh_token"
        payload = {"refresh_token": self._refresh_token}

        async with self._session.post(
            url, json=payload, headers=self._get_headers(use_auth=False)
        ) as response:
            if response.status == 200:
                data = await response.json()
                self._access_token = data["access_token"]
                self._refresh_token = data.get("refresh_token", self._refresh_token)
                self._token_expires_at = datetime.now() + timedelta(
                    seconds=data["expires_in"]
                )
                self._user_id = data["user"]["id"]
            else:
                raise AmbientOneAuthError("Failed to refresh access token")

    async def authenticate(self) -> None:
        """Authenticate with email and password."""
        url = f"{self.base_url}/auth/v1/token?grant_type=password"
        payload = {"email": self.email, "password": self.password}

        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            async with self._session.post(
                url, json=payload, headers=self._get_headers(use_auth=False)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self._access_token = data["access_token"]
                    self._refresh_token = data["refresh_token"]
                    self._token_expires_at = datetime.now() + timedelta(
                        seconds=data["expires_in"]
                    )
                    self._user_id = data["user"]["id"]
                    _LOGGER.debug("Successfully authenticated with Ambient One API")
                else:
                    error_text = await response.text()
                    raise AmbientOneAuthError(
                        f"Authentication failed: {response.status} - {error_text}"
                    )
        except aiohttp.ClientError as err:
            raise AmbientOneAPIError(f"Network error during authentication: {err}")

    async def get_devices(self) -> list[AmbientOneDevice]:
        """Get list of devices for the authenticated user."""
        await self._ensure_token_valid()

        url = (
            f"{self.base_url}/rest/v1/devices?"
            f"select=device_id,name,last_seen,firmware_version,space_id,location_id,"
            f"battery_percentage,wifi_rssi,organization_id,user_id,"
            f"spaces!devices_space_id_fkey(name),"
            f"locations!devices_location_id_fkey(name)"
            f"&user_id=eq.{self._user_id}"
            f"&order=last_seen.desc.nullslast"
        )

        try:
            async with self._session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    return [AmbientOneDevice(device) for device in data]
                else:
                    error_text = await response.text()
                    raise AmbientOneAPIError(
                        f"Failed to get devices: {response.status} - {error_text}"
                    )
        except aiohttp.ClientError as err:
            raise AmbientOneAPIError(f"Network error getting devices: {err}")

    async def get_sensor_data(
        self, device_id: str, realtime: bool = False
    ) -> AmbientOneSensorData | None:
        """Get sensor data for a device.

        Args:
            device_id: The device ID
            realtime: If True, get only IAQ score from realtime table.
                     If False, get full sensor data from latest sensor_averages.
        """
        await self._ensure_token_valid()

        if realtime:
            # Get just the IAQ score from realtime table
            url = (
                f"{self.base_url}/rest/v1/sensor_realtime?"
                f"select=device_id,iaq_score,timestamp"
                f"&device_id=eq.{device_id}"
            )
        else:
            # Get full sensor data from averages (last 5 minutes)
            url = (
                f"{self.base_url}/rest/v1/sensor_averages?"
                f"select=*"
                f"&device_id=eq.{device_id}"
                f"&aggregation_type=eq.minute"
                f"&order=timestamp.desc"
                f"&limit=1"
            )

        try:
            async with self._session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return AmbientOneSensorData(data[0])
                    return None
                else:
                    error_text = await response.text()
                    raise AmbientOneAPIError(
                        f"Failed to get sensor data: {response.status} - {error_text}"
                    )
        except aiohttp.ClientError as err:
            raise AmbientOneAPIError(f"Network error getting sensor data: {err}")

    async def get_device_events(
        self, device_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent air quality events for a device."""
        await self._ensure_token_valid()

        url = (
            f"{self.base_url}/rest/v1/device_events?"
            f"select=*"
            f"&device_id=eq.{device_id}"
            f"&order=timestamp.desc"
            f"&limit={limit}"
        )

        try:
            async with self._session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise AmbientOneAPIError(
                        f"Failed to get device events: {response.status} - {error_text}"
                    )
        except aiohttp.ClientError as err:
            raise AmbientOneAPIError(f"Network error getting device events: {err}")
