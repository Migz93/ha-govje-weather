"""Sensor platform for GOV.JE Weather integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
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
        name="GOV.JE Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data.get("currentTemprature", "0").replace("°C", "")) 
                if data.get("currentTemprature") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="uv_index",
        name="GOV.JE UV Index",
        icon="mdi:weather-sunny-alert",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("forecastDay", [])[0].get("uvIndex") if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="max_temp",
        name="GOV.JE Maximum Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data.get("forecastDay", [])[0].get("maxTemp", "0").replace("°C", "")) 
                if data.get("forecastDay") and data.get("forecastDay")[0].get("maxTemp") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="min_temp",
        name="GOV.JE Minimum Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: float(data.get("forecastDay", [])[0].get("minTemp", "0").replace("°C", ""))
                if data.get("forecastDay") and data.get("forecastDay")[0].get("minTemp") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_speed_mph",
        name="GOV.JE Wind Speed MPH",
        # Remove device_class to prevent automatic unit conversion
        icon="mdi:weather-windy",  # Add an icon since we're not using device_class
        native_unit_of_measurement="mph",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (
            # Determine which wind speed to use based on time of day
            int(data.get("forecastDay", [])[0].get(f"windspeedMph{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}", 0))
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_speed_knots",
        name="GOV.JE Wind Speed Knots",
        # Consistent with wind_speed_mph, no device_class to prevent automatic unit conversion
        icon="mdi:windsock",
        native_unit_of_measurement="knots",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (
            # Determine which wind speed to use based on time of day
            int(data.get("forecastDay", [])[0].get(
                f"windspeedKnots{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}", 0
            ))
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_direction",
        name="GOV.JE Wind Direction",
        icon="mdi:compass",
        value_fn=lambda data: (
            # Determine which wind direction to use based on time of day
            data.get("forecastDay", [])[0].get(
                f"windDirection{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}",
                data.get("forecastDay", [])[0].get("windDirection")
            )
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_force",
        name="GOV.JE Wind Force",
        icon="mdi:weather-windy",
        value_fn=lambda data: (
            # Determine which wind force to use based on time of day
            data.get("forecastDay", [])[0].get(
                f"windSpeedForce{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}",
                data.get("forecastDay", [])[0].get("windSpeed")
            )
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="rain_probability",
        name="GOV.JE Rain Probability",
        icon="mdi:weather-rainy",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (
            # Determine which rain probability to use based on time of day
            int(data.get("forecastDay", [])[0].get(
                f"rainProb{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}", 0
            ))
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="sunrise",
        name="GOV.JE Sunrise",
        icon="mdi:weather-sunset-up",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("sunRise")
                if data.get("forecastDay") else None,
    ),
    JerseyWeatherSensorEntityDescription(
        key="sunset",
        name="GOV.JE Sunset",
        icon="mdi:weather-sunset-down",
        value_fn=lambda data: data.get("forecastDay", [])[0].get("sunSet")
                if data.get("forecastDay") else None,
    ),

    JerseyWeatherSensorEntityDescription(
        key="forecast_summary",
        name="GOV.JE Forecast Summary",
        icon="mdi:text-box-outline",
        value_fn=lambda data: (
            # Determine which description to use based on time of day
            data.get("forecastDay", [])[0].get(
                f"{datetime.now().hour >= 18 and 'night' or datetime.now().hour >= 12 and 'afternoon' or 'morning'}Descripiton",
                None
            )
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="wind_speed_kph",
        name="GOV.JE Wind Speed KPH",
        icon="mdi:speedometer",
        native_unit_of_measurement="km/h",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (
            # Determine which wind speed to use based on time of day
            int(data.get("forecastDay", [])[0].get(
                f"windspeedKM{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}", 0
            ))
            if data.get("forecastDay") else None
        ),
    ),
    JerseyWeatherSensorEntityDescription(
        key="confidence",
        name="GOV.JE Confidence",
        icon="mdi:check-circle-outline",
        # Remove native_unit_of_measurement and state_class since this is a string value
        value_fn=lambda data: (
            # Determine which confidence to use based on time of day
            data.get("forecastDay", [])[0].get(
                f"confidence{datetime.now().hour >= 18 and 'Evening' or datetime.now().hour >= 12 and 'Afternoon' or 'Morning'}", 
                None
            )
            if data.get("forecastDay") else None
        ),
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
        # Set unique_id for entity registration
        self._attr_unique_id = f"govje_{description.key}"
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
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "wind_speed_knots":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "wind_speed_kph":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "wind_direction":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "wind_force":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "weather_description":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "confidence":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "rain_probability":
                # Skip adding attributes for this key as we handle it specially below
                continue
            elif key == "sunrise":
                value = day_data.get("sunRise")
            elif key == "sunset":
                value = day_data.get("sunSet")

            else:
                value = None
                
            if value is not None:
                attributes[day_name] = value
                
        # Special handling for time-of-day aware sensors to show all future periods
        # Helper function to add future periods for a given sensor type
        def add_future_periods(sensor_key, morning_key, afternoon_key, evening_key):
            # Determine current time of day
            current_hour = datetime.now().hour
            
            # Determine which periods to show
            show_morning = False  # Morning period is 00:00-11:59, already passed at this point
            show_afternoon = current_hour < 12  # Before noon, show today's afternoon
            show_evening = current_hour < 18  # Before 6pm, show today's evening
            
            # Get today's data
            today_data = self.coordinator.data.get("forecastDay", [])[0]
            today_name = today_data.get("dayName", "Today")
            
            # Add today's remaining periods
            if show_afternoon:
                attributes[f"{today_name} Afternoon"] = today_data.get(afternoon_key)
            if show_evening:
                attributes[f"{today_name} Evening"] = today_data.get(evening_key)
            
            # Add future days with all their periods
            for i in range(1, min(6, len(forecast_days))):
                day_data = forecast_days[i]
                day_name = day_data.get("dayName", day_data.get("day", f"Day {i+1}"))
                date_str = day_data.get("forecastDate", "")
                
                # Use date if available, otherwise just the day name
                prefix = date_str if date_str else day_name
                
                # Add all periods for future days
                attributes[f"{prefix} Morning"] = day_data.get(morning_key)
                attributes[f"{prefix} Afternoon"] = day_data.get(afternoon_key)
                attributes[f"{prefix} Evening"] = day_data.get(evening_key)
        
        # Handle each time-of-day aware sensor
        if key == "rain_probability":
            add_future_periods(key, "rainProbMorning", "rainProbAfternoon", "rainProbEvening")
        elif key == "wind_speed_mph":
            add_future_periods(key, "windspeedMphMorning", "windspeedMphAfternoon", "windspeedMphEvening")
        elif key == "wind_speed_knots":
            add_future_periods(key, "windspeedKnotsMorning", "windspeedKnotsAfternoon", "windspeedKnotsEvening")
        elif key == "wind_speed_kph":
            add_future_periods(key, "windspeedKMMorning", "windspeedKMAfternoon", "windspeedKMEvening")
        elif key == "wind_direction":
            add_future_periods(key, "windDirectionMorning", "windDirectionAfternoon", "windDirectionEvening")
        elif key == "wind_force":
            add_future_periods(key, "windSpeedForceMorning", "windSpeedForceAfternoon", "windSpeedForceEvening")
        elif key == "forecast_summary":
            add_future_periods(key, "morningDescripiton", "afternoonDescripiton", "nightDescripiton")
        elif key == "confidence":
            add_future_periods(key, "confidenceMorning", "confidenceAfternoon", "confidenceEvening")
        
        return attributes if attributes else None
