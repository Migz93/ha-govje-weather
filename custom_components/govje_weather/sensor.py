"""Sensor platform for GOV.JE Weather integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    GOVJE_COORDINATOR,
    GOVJE_NAME,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class JerseyWeatherSensorEntityDescription(SensorEntityDescription):
    """Class describing GOV.JE Weather sensor entities."""

    value_fn: Callable[[dict[str, Any]], StateType] = None


SENSOR_TYPES: tuple[JerseyWeatherSensorEntityDescription, ...] = (
    JerseyWeatherSensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data.get("currentTemprature", "0").replace("°C", "")) 
                if data.get("currentTemprature") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="uv_index",
        name="UV Index",
        icon="mdi:weather-sunny-alert",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("forecastDay", [])[0].get("uvIndex") if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="max_temp",
        name="Maximum Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data.get("forecastDay", [])[0].get("maxTemp", "0").replace("°C", "")) 
                if data.get("forecastDay") and data.get("forecastDay")[0].get("maxTemp") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="min_temp",
        name="Minimum Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data.get("forecastDay", [])[0].get("minTemp", "0").replace("°C", ""))
                if data.get("forecastDay") and data.get("forecastDay")[0].get("minTemp") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_speed_mph",
        name="Wind Speed MPH",
        # Remove device_class to prevent automatic unit conversion
        icon="mdi:weather-windy",  # Add an icon since we're not using device_class
        native_unit_of_measurement="mph",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("forecastDay", [])[0].get("windSpeedMPH", 0))
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_speed_knots",
        name="Wind Speed Knots",
        # Consistent with wind_speed_mph, no device_class to prevent automatic unit conversion
        icon="mdi:windsock",
        native_unit_of_measurement="knots",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("forecastDay", [])[0].get("windSpeedKnots", 0))
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_direction",
        name="Wind Direction",
        icon="mdi:compass",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("windDirection")
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_force",
        name="Wind Force",
        icon="mdi:weather-windy",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("windSpeed")
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="rain_probability_morning",
        name="Rain Probability Morning",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("forecastDay", [])[0].get("rainProbMorning", 0))
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="rain_probability_afternoon",
        name="Rain Probability Afternoon",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("forecastDay", [])[0].get("rainProbAfternoon", 0))
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="rain_probability_evening",
        name="Rain Probability Evening",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: int(data.get("forecastDay", [])[0].get("rainProbEvening", 0))
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="sunrise",
        name="Sunrise",
        icon="mdi:weather-sunset-up",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("sunRise")
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="sunset",
        name="Sunset",
        icon="mdi:weather-sunset-down",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("sunSet")
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="forecast_summary",
        name="Forecast Summary",
        icon="mdi:text-box-outline",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("summary")
                if data.get("forecastDay") else None,
    ),
    # Forecast Date and Forecast Time entities removed as requested
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up GOV.JE Weather sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass_data[GOVJE_COORDINATOR]
    name = hass_data[GOVJE_NAME]

    entities = []
    
    # Create sensor entities
    for description in SENSOR_TYPES:
        entities.append(
            JerseyWeatherSensor(
                coordinator=coordinator,
                name=name,
                description=description,
            )
        )

    async_add_entities(entities)


class JerseyWeatherSensor(
    CoordinatorEntity[DataUpdateCoordinator], SensorEntity
):
    """Implementation of a GOV.JE Weather sensor."""

    entity_description: JerseyWeatherSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        description: JerseyWeatherSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{name}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{name}")},
            "name": name,  # Use the name as-is without appending 'Weather'
            "manufacturer": "Government of Jersey",
            "model": "Weather Forecast",
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        return self.entity_description.value_fn(self.coordinator.data)
        
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return entity specific state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("forecastDay"):
            return None
            
        # Get the key from the entity description to know which attribute to extract
        key = self.entity_description.key
        forecast_days = self.coordinator.data.get("forecastDay", [])
        
        # Skip if we don't have enough forecast days
        if len(forecast_days) <= 1:
            return None
            
        attributes = {}
        
        # Add forecast data for the next 5 days (or fewer if not available)
        for i in range(1, min(6, len(forecast_days))):
            day_data = forecast_days[i]
            day_name = day_data.get("dayName", day_data.get("day", f"Day {i+1}"))
            
            # Extract the appropriate value based on the sensor type
            if key == "uv_index":
                value = day_data.get("uvIndex")
            elif key == "max_temp":
                temp = day_data.get("maxTemp")
                value = float(temp.replace("°C", "")) if temp else None
            elif key == "min_temp":
                temp = day_data.get("minTemp")
                value = float(temp.replace("°C", "")) if temp else None
            elif key == "wind_speed_mph":
                value = day_data.get("windSpeedMPH")
            elif key == "wind_speed_knots":
                value = day_data.get("windSpeedKnots")
            elif key == "wind_direction":
                value = day_data.get("windDirection")
            elif key == "wind_force":
                value = day_data.get("windSpeed")
            elif key == "rain_probability_morning":
                value = day_data.get("rainProbMorning")
            elif key == "rain_probability_afternoon":
                value = day_data.get("rainProbAfternoon")
            elif key == "rain_probability_evening":
                value = day_data.get("rainProbEvening")
            elif key == "sunrise":
                value = day_data.get("sunRise")
            elif key == "sunset":
                value = day_data.get("sunSet")
            elif key == "forecast_summary":
                value = day_data.get("summary")
            else:
                value = None
                
            if value is not None:
                attributes[day_name] = value
                
        return attributes if attributes else None
