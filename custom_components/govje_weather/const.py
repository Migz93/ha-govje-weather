"""Constants for GOV.JE Weather Integration."""
from datetime import timedelta

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_LIGHTNING_RAINY,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
    ATTR_CONDITION_WINDY_VARIANT,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
)

DOMAIN = "govje_weather"

DEFAULT_NAME = "GOV.JE Weather"
ATTRIBUTION = "Data provided by Government of Jersey"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)
MIN_SCAN_INTERVAL = 5  # minutes
MAX_SCAN_INTERVAL = 1440  # minutes (1 day)

# Configuration and options
CONF_LOCATION = "location"

# Coordinator names
GOVJE_COORDINATOR = "govje_coordinator"
GOVJE_NAME = "govje_name"

# Data source
REMOTE_URL = "https://prodgojweatherstorage.blob.core.windows.net/data/jerseyForecast.json"

# Home Assistant weather conditions reference:
# 'clear-night' - Clear, night: The sky is clear during the night. .
# 'cloudy' - Cloudy: There are many clouds in the sky.
# 'fog' - Fog: There is a thick mist or fog reducing visibility.
# 'hail' - Hail: Hailstones are falling.
# 'lightning' - Lightning: Lightning/thunderstorms are occurring.
# 'lightning-rainy' - Lightning, rainy: Lightning/thunderstorm is occurring along with rain.
# 'partlycloudy' - Partly cloudy: The sky is partially covered with clouds.
# 'pouring' - Pouring: It is raining heavily.
# 'rainy' - Rainy: It is raining.
# 'snowy' - Snowy: It is snowing.
# 'snowy-rainy' - Snowy, rainy: It is snowing and raining at the same time.
# 'sunny' - Sunny: The sky is clear and the sun is shining.
# 'windy' - Windy: It is windy. windy.
# 'windy-variant' - Windy, cloudy: It is windy and cloudy.
# 'exceptional' - Exceptional: Exceptional weather conditions are occurring.
#
# Reference: https://www.home-assistant.io/integrations/weather/#condition-mapping

# Tooltip mappings based on the dayToolTip values in the JSON data
# Map the tooltip text to Home Assistant weather conditions
TOOLTIP_CONDITION_MAP = {
    "Sunny": ATTR_CONDITION_SUNNY,
    "Sunny and hot": ATTR_CONDITION_SUNNY,
    "Mainly sunny": ATTR_CONDITION_PARTLYCLOUDY,
    "Fine": ATTR_CONDITION_CLEAR_NIGHT,
    "Sunny periods": ATTR_CONDITION_PARTLYCLOUDY,
    "Cloudy, a few brighter spells": ATTR_CONDITION_PARTLYCLOUDY,
    "Cloudy a.m. Sunny p.m.": ATTR_CONDITION_PARTLYCLOUDY,
    "Sunny a.m. Cloudy p.m.": ATTR_CONDITION_PARTLYCLOUDY,
    "Sunny a.m. Rain p.m.": ATTR_CONDITION_RAINY,
    "Rain later": ATTR_CONDITION_RAINY,
    "Rain a.m. Sunny p.m.": ATTR_CONDITION_RAINY,
    "Rain": ATTR_CONDITION_RAINY,
    "Fair": ATTR_CONDITION_PARTLYCLOUDY,
    "Sunshine and showers": ATTR_CONDITION_RAINY,
    "Sunshine and heavy shower": ATTR_CONDITION_RAINY,
    "Cloudy with showers": ATTR_CONDITION_RAINY,
    "Rain at times": ATTR_CONDITION_POURING,
    "Cloudy": ATTR_CONDITION_CLOUDY,
    # Add more mappings as needed based on the full set of tooltips
}

# Wind direction mappings
WIND_DIRECTION_MAP = {
    "N": 0,
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSW": 202.5,
    "SW": 225,
    "WSW": 247.5,
    "W": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5,
}

# Wind force to speed conversion (approximate values in m/s)
WIND_FORCE_TO_SPEED = {
    "F0": 0.0,      # Calm
    "F1": 0.5,      # Light air
    "F2": 2.0,      # Light breeze
    "F3": 4.0,      # Gentle breeze
    "F4": 6.0,      # Moderate breeze
    "F5": 9.0,      # Fresh breeze
    "F6": 12.0,     # Strong breeze
    "F7": 15.0,     # Near gale
    "F8": 19.0,     # Gale
    "F9": 23.0,     # Strong gale
    "F10": 27.0,    # Storm
    "F11": 31.0,    # Violent storm
    "F12": 34.0,    # Hurricane
}
