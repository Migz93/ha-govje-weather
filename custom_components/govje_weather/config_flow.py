"""Config flow for GOV.JE Weather integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default=DEFAULT_NAME): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GOV.JE Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Use name as the unique ID
        await self.async_set_unique_id(user_input["name"])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=user_input["name"],
            data={},
            options={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Validate scan_interval is within allowed range
            scan_interval = user_input.get("scan_interval")
            if scan_interval < MIN_SCAN_INTERVAL:
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                "scan_interval",
                                default=MIN_SCAN_INTERVAL,
                            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
                        }
                    ),
                    errors={"scan_interval": f"Value must be at least {MIN_SCAN_INTERVAL}"},
                )
            if scan_interval > MAX_SCAN_INTERVAL:
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Required(
                                "scan_interval",
                                default=MAX_SCAN_INTERVAL,
                            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
                        }
                    ),
                    errors={"scan_interval": f"Value must be at most {MAX_SCAN_INTERVAL}"},
                )
            return self.async_create_entry(title="", data=user_input)

        # Get current scan_interval or use default
        current_scan_interval = self.config_entry.options.get(
            "scan_interval", DEFAULT_SCAN_INTERVAL.total_seconds() // 60
        )

        options = {
            vol.Required(
                "scan_interval",
                default=current_scan_interval,
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
