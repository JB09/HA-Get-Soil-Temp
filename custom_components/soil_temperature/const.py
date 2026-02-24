"""Constants for the Soil Temperature integration."""

from datetime import timedelta

DOMAIN = "soil_temperature"

SCAN_INTERVAL = timedelta(minutes=30)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CONF_ZONE = "zone"
CONF_DEPTHS = "depths"

SOIL_DEPTHS = [0, 6, 18, 54]
DEFAULT_DEPTHS = [6]


def build_hourly_params(depths: list[int]) -> str:
    """Build the Open-Meteo hourly parameter string for the given depths."""
    return ",".join(f"soil_temperature_{d}cm" for d in depths)
