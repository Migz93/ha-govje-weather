"""Weather entity for GOV.JE Weather integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import re
import logging
from typing import Any, cast

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_IS_DAYTIME,
    DOMAIN as WEATHER_DOMAIN,
    CoordinatorWeatherEntity,
    Forecast,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    ATTRIBUTION,
    DOMAIN,
    GOVJE_COORDINATOR,
    GOVJE_NAME,
    ICON_CONDITION_MAP,
    WIND_DIRECTION_MAP,
    WIND_FORCE_TO_SPEED,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the GOV.JE Weather weather platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass_data[GOVJE_COORDINATOR]
    name = hass_data[GOVJE_NAME]

    async_add_entities([JerseyWeather(coordinator, name)], False)


def _get_condition_from_icon(icon: str) -> str | None:
    """Map the icon to a condition."""
    return ICON_CONDITION_MAP.get(icon)


def _get_wind_bearing_from_direction(direction: str) -> float | None:
    """Convert wind direction to bearing degrees."""
    return WIND_DIRECTION_MAP.get(direction)


def _get_wind_speed_from_force(force: str) -> float | None:
    """Convert wind force to speed in m/s."""
    return WIND_FORCE_TO_SPEED.get(force)


def _extract_temp_value(temp_str: str) -> float | None:
    """Extract temperature value from string like '24°C'."""
    if not temp_str:
        return None
    try:
        return float(temp_str.replace("°C", ""))
    except (ValueError, TypeError):
        return None


def _parse_day_name_to_date(day_name: str, forecast_date: str = None) -> str:
    """Parse a day name like 'Today' or 'Sat 12 Jul' into an ISO date."""
    now = datetime.now()
    
    # If it's 'Today', use the current date
    if day_name == "Today":
        return now.strftime("%Y-%m-%dT12:00:00")
    
    # If it's 'Tomorrow', use tomorrow's date
    if day_name == "Tomorrow":
        tomorrow = now + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%dT12:00:00")
    
    # Try to parse formats like 'Sat 12 Jul'
    if day_name:
        # Extract day and month
        match = re.match(r'\w+ (\d+) (\w+)', day_name)
        if match:
            day = int(match.group(1))
            month_str = match.group(2)
            
            # Map month abbreviation to month number
            month_map = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            month = month_map.get(month_str, now.month)
            
            # Determine year (assume current year, but handle December-January transition)
            year = now.year
            if month < now.month and month in [1, 2]:  # January or February when current month is later
                year += 1
            
            # Create the date
            try:
                forecast_date = datetime(year, month, day, 12, 0, 0)
                return forecast_date.strftime("%Y-%m-%dT12:00:00")
            except ValueError:
                pass
    
    # If we have a forecast date from the JSON (format: "11 July 2025")
    if forecast_date:
        try:
            # Try to parse the forecast date
            parsed_date = datetime.strptime(forecast_date, "%d %B %Y")
            return parsed_date.strftime("%Y-%m-%dT12:00:00")
        except ValueError:
            pass
    
    # Fallback: use current date
    return now.strftime("%Y-%m-%dT12:00:00")


def _build_forecast_data(day_data: dict[str, Any], is_today: bool = False, forecast_date: str = None) -> Forecast:
    """Build forecast data for a day."""
    # Parse date from dayName
    day_name = day_data.get("dayName")
    
    # Create ISO format datetime string
    datetime_str = _parse_day_name_to_date(day_name, forecast_date)
    
    # Create forecast data
    forecast_data = Forecast(
        datetime=datetime_str,
    )
    
    # Map condition from dayIcon
    day_icon = day_data.get("dayIcon")
    if day_icon:
        condition = _get_condition_from_icon(day_icon)
        if condition:
            forecast_data[ATTR_FORECAST_CONDITION] = condition
    
    # Temperature
    max_temp = _extract_temp_value(day_data.get("maxTemp"))
    min_temp = _extract_temp_value(day_data.get("minTemp"))
    
    if max_temp is not None:
        forecast_data[ATTR_FORECAST_NATIVE_TEMP] = max_temp
    
    if min_temp is not None:
        forecast_data[ATTR_FORECAST_NATIVE_TEMP_LOW] = min_temp
    
    # Precipitation probability (use highest of morning/afternoon/evening)
    precip_probs = [
        int(day_data.get("rainProbMorning", 0)),
        int(day_data.get("rainProbAfternoon", 0)),
        int(day_data.get("rainProbEvening", 0)),
    ]
    max_precip_prob = max(precip_probs)
    forecast_data[ATTR_FORECAST_PRECIPITATION_PROBABILITY] = max_precip_prob
    
    # Wind
    wind_direction = day_data.get("windDirection")
    if wind_direction:
        bearing = _get_wind_bearing_from_direction(wind_direction)
        if bearing is not None:
            forecast_data[ATTR_FORECAST_WIND_BEARING] = bearing
    
    wind_force = day_data.get("windSpeed")
    if wind_force:
        speed = _get_wind_speed_from_force(wind_force)
        if speed is not None:
            forecast_data[ATTR_FORECAST_NATIVE_WIND_SPEED] = speed
    
    # Mark as daytime forecast
    forecast_data[ATTR_FORECAST_IS_DAYTIME] = True
    
    return forecast_data


class JerseyWeather(CoordinatorWeatherEntity):
    """Representation of Jersey Weather."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.MILES_PER_HOUR
    _attr_attribution = ATTRIBUTION
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
    ) -> None:
        """Initialize the platform with a data instance."""
        super().__init__(coordinator)
        self._attr_unique_id = "govje"
        self._attr_name = "GOV.JE"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{name}")},
            "name": name,  # Use the name as-is without appending 'Weather'
            "manufacturer": "Government of Jersey",
            "model": "Weather Forecast",
        }

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data:
            return None
            
        # Get current condition from the first day's icon
        try:
            day_data = self.coordinator.data.get("forecastDay", [])[0]
            icon = day_data.get("dayIcon")
            return _get_condition_from_icon(icon)
        except (IndexError, KeyError):
            return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        if not self.coordinator.data:
            return None
            
        temp_str = self.coordinator.data.get("currentTemprature")
        return _extract_temp_value(temp_str)

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind bearing."""
        if not self.coordinator.data:
            return None
            
        try:
            day_data = self.coordinator.data.get("forecastDay", [])[0]
            wind_direction = day_data.get("windDirection")
            return _get_wind_bearing_from_direction(wind_direction)
        except (IndexError, KeyError):
            return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        if not self.coordinator.data:
            return None
            
        try:
            day_data = self.coordinator.data.get("forecastDay", [])[0]
            wind_force = day_data.get("windSpeed")
            return _get_wind_speed_from_force(wind_force)
        except (IndexError, KeyError):
            return None

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast in native units."""
        if not self.coordinator.data:
            return None
            
        forecast_days = self.coordinator.data.get("forecastDay", [])
        if not forecast_days:
            return None
            
        # Get the main forecast date from the data
        forecast_date = self.coordinator.data.get("forecastDate")
        
        forecasts = []
        
        # Process each day in the forecast
        for i, day_data in enumerate(forecast_days):
            forecast = _build_forecast_data(day_data, is_today=(i == 0), forecast_date=forecast_date)
            forecasts.append(forecast)
            
        return forecasts
