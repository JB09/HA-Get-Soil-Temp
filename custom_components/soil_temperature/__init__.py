"""The Soil Temperature integration."""

from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_DEPTHS, SOIL_DEPTHS
from .coordinator import SoilTemperatureConfigEntry, SoilTemperatureCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_migrate_entry(
    hass: HomeAssistant, config_entry: SoilTemperatureConfigEntry
) -> bool:
    """Migrate old entry to new version."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version > 2:
        return False

    if config_entry.version == 1:
        # v1 entries have no depth selection — enable ALL depths
        # to preserve existing behavior for upgrading users.
        hass.config_entries.async_update_entry(
            config_entry,
            options={CONF_DEPTHS: list(SOIL_DEPTHS)},
            version=2,
            minor_version=1,
        )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: SoilTemperatureConfigEntry
) -> None:
    """Handle options update by reloading the entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(
    hass: HomeAssistant, entry: SoilTemperatureConfigEntry
) -> bool:
    """Set up Soil Temperature from a config entry."""
    coordinator = SoilTemperatureCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.async_add_import_executor_job(
        __import__, "custom_components.soil_temperature.sensor"
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SoilTemperatureConfigEntry
) -> bool:
    """Unload a Soil Temperature config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
