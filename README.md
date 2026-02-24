# Soil Temperature for Home Assistant

A custom Home Assistant integration that provides soil temperature data at multiple depths using the [Open-Meteo](https://open-meteo.com/) free API.

## Features

- Soil temperature at up to 4 depths: 0cm (surface), 6cm, 18cm, and 54cm
- **Configurable depth selection** — choose which depths to monitor during setup or later via options
- Current temperature, 24-hour average, and 5-day average for each selected depth
- 7-day daily forecast included as sensor attributes
- Zone-based configuration (uses your HA zone's coordinates)
- 30-minute polling interval
- HACS compatible

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (top right) → **Custom repositories**
3. Add `https://github.com/JB09/HA-Get-Soil-Temp` as an **Integration**
4. Search for "Soil Temperature" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/soil_temperature` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Soil Temperature**
3. Select a zone (e.g., "Home") — the integration uses the zone's latitude/longitude
4. Select which soil depths to monitor (6cm is selected by default)
5. Done! 3 sensors are created per selected depth

### Changing Depths After Setup

Go to **Settings** → **Devices & Services**, find the Soil Temperature integration, and click **Configure**. You can add or remove depths at any time — the integration will reload and update the sensors automatically.

## Sensors

For each selected soil depth, three sensors are created:

| Sensor | Description |
|--------|-------------|
| Current | Latest hourly soil temperature reading |
| 24h Average | Mean temperature over the last 24 hours |
| 5-Day Average | Mean temperature over the last 5 days |

The 6cm depth sensors use simplified names (e.g., "Soil Temperature Current") since this is the most commonly referenced depth for gardening and agriculture.

Current temperature sensors include a 7-day daily forecast as extra state attributes (e.g., `forecast_2024-03-15: 52.3`).

All temperatures are reported in Celsius. Home Assistant will automatically convert to Fahrenheit if your system is configured for imperial units.

## Upgrading from a Previous Version

If you are upgrading from a version that did not support depth selection, all four depths (0cm, 6cm, 18cm, 54cm) will remain enabled automatically — no existing sensors are lost. You can then go to **Configure** to deselect any depths you don't need.

## Data Source

This integration uses the free [Open-Meteo API](https://open-meteo.com/en/docs) which provides:

- Hourly soil temperature data at 0cm, 6cm, 18cm, and 54cm depths
- Up to 16 days of forecast data
- 5 days of historical data
- No API key required

## Multiple Locations

To monitor soil temperature at different locations, simply add the integration multiple times — each with a different zone. Create custom zones in Home Assistant under **Settings** → **Areas & Zones** → **Zones**.
