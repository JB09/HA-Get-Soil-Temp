"""Data update coordinator for the Soil Temperature integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from statistics import mean
from typing import TypeAlias

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ZONE,
    DOMAIN,
    HOURLY_PARAMS,
    OPEN_METEO_FORECAST_URL,
    SCAN_INTERVAL,
    SOIL_DEPTHS,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class SoilDepthData:
    """Data for a single soil depth."""

    current: float | None = None
    avg_24h: float | None = None
    avg_5day: float | None = None
    forecast_daily: dict[str, float] = field(default_factory=dict)


@dataclass
class SoilTemperatureData:
    """Aggregated soil temperature data for all depths."""

    depths: dict[int, SoilDepthData] = field(default_factory=dict)


class SoilTemperatureCoordinator(DataUpdateCoordinator[SoilTemperatureData]):
    """Coordinator to fetch and process soil temperature data from Open-Meteo."""

    config_entry: SoilTemperatureConfigEntry

    def __init__(self, hass: HomeAssistant, entry: SoilTemperatureConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
        )
        self._zone_entity_id: str = entry.data[CONF_ZONE]

    def _get_zone_coordinates(self) -> tuple[float, float]:
        """Resolve lat/lon from the configured zone entity."""
        state = self.hass.states.get(self._zone_entity_id)
        if state is None:
            raise UpdateFailed(
                f"Zone entity {self._zone_entity_id} not found"
            )
        latitude = state.attributes.get("latitude")
        longitude = state.attributes.get("longitude")
        if latitude is None or longitude is None:
            raise UpdateFailed(
                f"Zone entity {self._zone_entity_id} has no coordinates"
            )
        return float(latitude), float(longitude)

    async def _async_update_data(self) -> SoilTemperatureData:
        """Fetch soil temperature data from Open-Meteo and compute averages."""
        latitude, longitude = self._get_zone_coordinates()

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": HOURLY_PARAMS,
            "past_days": 5,
            "forecast_days": 7,
            "temperature_unit": "fahrenheit",
            "timezone": "auto",
        }

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                OPEN_METEO_FORECAST_URL, params=params
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Open-Meteo API returned status {response.status}"
                    )
                data = await response.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching data from Open-Meteo: {err}") from err

        return self._process_response(data)

    def _process_response(self, data: dict) -> SoilTemperatureData:
        """Process the Open-Meteo API response into structured data."""
        hourly = data.get("hourly", {})
        time_list = hourly.get("time", [])

        if not time_list:
            raise UpdateFailed("No hourly data returned from Open-Meteo")

        now = datetime.now()
        result = SoilTemperatureData()

        for depth in SOIL_DEPTHS:
            key = f"soil_temperature_{depth}cm"
            values = hourly.get(key, [])

            if not values:
                result.depths[depth] = SoilDepthData()
                continue

            # Pair timestamps with values, filtering out nulls
            paired = []
            for i, t in enumerate(time_list):
                if i < len(values) and values[i] is not None:
                    ts = datetime.fromisoformat(t)
                    paired.append((ts, values[i]))

            if not paired:
                result.depths[depth] = SoilDepthData()
                continue

            # Current: most recent value at or before now
            past_values = [(ts, v) for ts, v in paired if ts <= now]
            current = past_values[-1][1] if past_values else paired[0][1]

            # 24h average: values from the last 24 hours
            cutoff_24h = now - timedelta(hours=24)
            vals_24h = [v for ts, v in paired if cutoff_24h <= ts <= now]
            avg_24h = round(mean(vals_24h), 1) if vals_24h else None

            # 5-day average: values from the last 5 days
            cutoff_5day = now - timedelta(days=5)
            vals_5day = [v for ts, v in paired if cutoff_5day <= ts <= now]
            avg_5day = round(mean(vals_5day), 1) if vals_5day else None

            # Daily forecast: average per future day
            daily_buckets: dict[str, list[float]] = {}
            future_values = [(ts, v) for ts, v in paired if ts > now]
            for ts, v in future_values:
                date_str = ts.strftime("%Y-%m-%d")
                daily_buckets.setdefault(date_str, []).append(v)
            forecast_daily = {
                d: round(mean(vs), 1) for d, vs in daily_buckets.items()
            }

            result.depths[depth] = SoilDepthData(
                current=current,
                avg_24h=avg_24h,
                avg_5day=avg_5day,
                forecast_daily=forecast_daily,
            )

        return result


SoilTemperatureConfigEntry: TypeAlias = ConfigEntry[SoilTemperatureCoordinator]
