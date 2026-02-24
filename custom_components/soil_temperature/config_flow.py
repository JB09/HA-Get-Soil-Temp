"""Config flow for the Soil Temperature integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.zone import DOMAIN as ZONE_DOMAIN
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import CONF_ZONE, DOMAIN


class SoilTemperatureFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Soil Temperature."""

    VERSION = 1

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
                await self.async_set_unique_id(user_input[CONF_ZONE])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=state.name,
                    data={CONF_ZONE: user_input[CONF_ZONE]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ZONE): EntitySelector(
                        EntitySelectorConfig(domain=ZONE_DOMAIN),
                    ),
                }
            ),
            errors=errors,
        )
