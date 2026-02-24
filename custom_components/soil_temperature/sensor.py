"""Sensor platform for the Soil Temperature integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import SOIL_DEPTHS
from .coordinator import (
    SoilTemperatureConfigEntry,
    SoilTemperatureCoordinator,
    SoilTemperatureData,
)


@dataclass(frozen=True, kw_only=True)
class SoilTemperatureSensorEntityDescription(SensorEntityDescription):
    """Describe a Soil Temperature sensor entity."""

    value_fn: Callable[[SoilTemperatureData, int], float | None]
    depth_cm: int
    include_forecast_attrs: bool = False


def _build_sensor_descriptions() -> list[SoilTemperatureSensorEntityDescription]:
    """Build sensor descriptions for all depths and metric types."""
    descriptions: list[SoilTemperatureSensorEntityDescription] = []

    for depth in SOIL_DEPTHS:
        # Use cleaner names for 6cm (the most commonly referenced depth)
        if depth == 6:
            name_prefix = "Soil Temperature"
            key_prefix = "soil_temp"
        else:
            name_prefix = f"Soil Temperature {depth}cm"
            key_prefix = f"soil_temp_{depth}cm"

        descriptions.extend(
            [
                SoilTemperatureSensorEntityDescription(
                    key=f"{key_prefix}_current",
                    name=f"{name_prefix} Current",
                    value_fn=lambda data, d=depth: (
                        data.depths[d].current if d in data.depths else None
                    ),
                    depth_cm=depth,
                    include_forecast_attrs=True,
                ),
                SoilTemperatureSensorEntityDescription(
                    key=f"{key_prefix}_24h_avg",
                    name=f"{name_prefix} 24h Average",
                    value_fn=lambda data, d=depth: (
                        data.depths[d].avg_24h if d in data.depths else None
                    ),
                    depth_cm=depth,
                ),
                SoilTemperatureSensorEntityDescription(
                    key=f"{key_prefix}_5day_avg",
                    name=f"{name_prefix} 5-Day Average",
                    value_fn=lambda data, d=depth: (
                        data.depths[d].avg_5day if d in data.depths else None
                    ),
                    depth_cm=depth,
                ),
            ]
        )

    return descriptions


SENSOR_DESCRIPTIONS = _build_sensor_descriptions()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SoilTemperatureConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Soil Temperature sensors from a config entry."""
    coordinator: SoilTemperatureCoordinator = entry.runtime_data

    async_add_entities(
        SoilTemperatureSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class SoilTemperatureSensor(
    CoordinatorEntity[SoilTemperatureCoordinator], SensorEntity
):
    """Representation of a Soil Temperature sensor."""

    entity_description: SoilTemperatureSensorEntityDescription

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator: SoilTemperatureCoordinator,
        description: SoilTemperatureSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, str | float] | None:
        """Return extra state attributes including forecast data."""
        if not self.entity_description.include_forecast_attrs:
            return None
        if self.coordinator.data is None:
            return None
        depth = self.entity_description.depth_cm
        depth_data = self.coordinator.data.depths.get(depth)
        if depth_data is None or not depth_data.forecast_daily:
            return None
        attrs: dict[str, str | float] = {}
        for date_str, temp in depth_data.forecast_daily.items():
            attrs[f"forecast_{date_str}"] = temp
        return attrs
