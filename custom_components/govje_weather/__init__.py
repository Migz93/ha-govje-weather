"""The GOV.JE Weather integration."""
from __future__ import annotations

import logging
import aiohttp
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    GOVJE_COORDINATOR,
    GOVJE_NAME,
    REMOTE_URL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GOV.JE Weather from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Get scan interval from options or use default
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL.total_seconds() // 60)
    scan_interval_timedelta = timedelta(minutes=scan_interval)
    
    # Create data coordinator
    coordinator = JerseyWeatherDataCoordinator(
        hass=hass,
        update_interval=scan_interval_timedelta
    )
    
    # Initial data fetch
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator reference
    hass.data[DOMAIN][entry.entry_id] = {
        GOVJE_COORDINATOR: coordinator,
        GOVJE_NAME: entry.title,
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Add update listener for options
    entry.async_on_unload(entry.add_update_listener(update_listener))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener for options."""
    # Get the coordinator
    coordinator = hass.data[DOMAIN][entry.entry_id][GOVJE_COORDINATOR]
    
    # Get new scan interval from options
    scan_interval = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL.total_seconds() // 60)
    scan_interval_timedelta = timedelta(minutes=scan_interval)
    
    # Update coordinator's update interval
    coordinator.update_interval = scan_interval_timedelta
    
    # Schedule next update with new interval
    coordinator.async_schedule_refresh()
    
    _LOGGER.debug("Updated scan interval to %s minutes", scan_interval)


class JerseyWeatherDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching GOV.JE weather data."""

    def __init__(self, hass: HomeAssistant, update_interval: timedelta = DEFAULT_SCAN_INTERVAL) -> None:
        """Initialize the data coordinator."""
        self.hass = hass
        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from GOV.JE Weather API."""
        try:
            return await self._fetch_remote_data()
        except Exception as err:
            raise UpdateFailed(f"Error updating Jersey weather data: {err}") from err

    async def _fetch_remote_data(self):
        """Fetch data from remote URL."""
        try:
            async with self.session.get(REMOTE_URL) as resp:
                if resp.status != 200:
                    _LOGGER.error(
                        "Error fetching Jersey weather data: %s", resp.status
                    )
                    raise UpdateFailed(f"Error fetching data: {resp.status}")
                
                data = await resp.json()
                return data
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching Jersey weather data: %s", err)
            raise
