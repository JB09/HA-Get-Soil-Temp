"""Config flow for the Soil Temperature integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.zone import DOMAIN as ZONE_DOMAIN
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import (
    CONF_DEPTHS,
    CONF_STATIC_FORECAST_ATTRS,
    CONF_ZONE,
    DEFAULT_DEPTHS,
    DOMAIN,
    SOIL_DEPTHS,
)

DEPTH_OPTIONS = {str(d): f"{d} cm" for d in SOIL_DEPTHS}


class SoilTemperatureFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Soil Temperature."""

    VERSION = 2
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            state = self.hass.states.get(user_input[CONF_ZONE])
            if (
                state is None
                or state.attributes.get("latitude") is None
                or state.attributes.get("longitude") is None
            ):
                errors["base"] = "no_coordinates"
            else:
                selected_depths = sorted(
                    int(d)
                    for d in user_input.get(
                        CONF_DEPTHS, [str(d) for d in DEFAULT_DEPTHS]
                    )
                )
                if not selected_depths:
                    errors["base"] = "no_depths"
                else:
                    await self.async_set_unique_id(user_input[CONF_ZONE])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=state.name,
                        data={CONF_ZONE: user_input[CONF_ZONE]},
                        options={CONF_DEPTHS: selected_depths},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ZONE): EntitySelector(
                        EntitySelectorConfig(domain=ZONE_DOMAIN),
                    ),
                    vol.Optional(
                        CONF_DEPTHS,
                        default=[str(d) for d in DEFAULT_DEPTHS],
                    ): cv.multi_select(DEPTH_OPTIONS),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SoilTemperatureOptionsFlowHandler:
        """Create the options flow."""
        return SoilTemperatureOptionsFlowHandler()


class SoilTemperatureOptionsFlowHandler(OptionsFlow):
    """Options flow handler for Soil Temperature."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            selected_depths = sorted(
                int(d) for d in user_input.get(CONF_DEPTHS, [])
            )
            if not selected_depths:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._build_schema(),
                    errors={"base": "no_depths"},
                )
            return self.async_create_entry(
                data={
                    CONF_DEPTHS: selected_depths,
                    CONF_STATIC_FORECAST_ATTRS: user_input.get(
                        CONF_STATIC_FORECAST_ATTRS, False
                    ),
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_schema(),
        )

    def _build_schema(self) -> vol.Schema:
        """Build the options schema with current selections as defaults."""
        current_depths = self.config_entry.options.get(
            CONF_DEPTHS, DEFAULT_DEPTHS
        )
        current_static = self.config_entry.options.get(
            CONF_STATIC_FORECAST_ATTRS, False
        )
        return vol.Schema(
            {
                vol.Optional(
                    CONF_DEPTHS,
                    default=[str(d) for d in current_depths],
                ): cv.multi_select(DEPTH_OPTIONS),
                vol.Optional(
                    CONF_STATIC_FORECAST_ATTRS,
                    default=current_static,
                ): bool,
            }
        )
