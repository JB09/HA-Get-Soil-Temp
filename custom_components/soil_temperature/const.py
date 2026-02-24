"""Constants for the Soil Temperature integration."""

from datetime import timedelta

DOMAIN = "soil_temperature"

SCAN_INTERVAL = timedelta(minutes=30)

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CONF_ZONE = "zone"

SOIL_DEPTHS = [0, 6, 18, 54]

HOURLY_PARAMS = ",".join(f"soil_temperature_{d}cm" for d in SOIL_DEPTHS)
