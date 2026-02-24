"""The Soil Temperature integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import SoilTemperatureConfigEntry, SoilTemperatureCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: SoilTemperatureConfigEntry
) -> bool:
    """Set up Soil Temperature from a config entry."""
    coordinator = SoilTemperatureCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SoilTemperatureConfigEntry
) -> bool:
    """Unload a Soil Temperature config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
