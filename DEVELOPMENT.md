# GOV.JE Weather Integration Development Guide

This document provides information about developing and maintaining the GOV.JE Weather integration for Home Assistant.

## Project Structure

The integration is organized as follows:

```
custom_components/govje_weather/
├── __init__.py        # Main integration setup and coordinator
├── const.py           # Constants used throughout the integration
├── manifest.json      # Integration metadata
├── sensor.py          # Sensor entity implementations
├── weather.py         # Weather entity implementation
└── translations/      # Localization files (if any)
```

## File Descriptions

### `__init__.py`

This file is the entry point for the integration. It contains:
- Integration setup code (`async_setup` and `async_setup_entry`)
- Data coordinator implementation that fetches JSON data from the GOV.JE weather API
- Platform setup for weather and sensor entities

The coordinator is responsible for fetching data from the API and providing it to all entities, ensuring efficient data retrieval.

### `const.py`

Contains constants used throughout the integration:
- Domain name
- API URLs
- Icon mappings
- Wind direction mappings
- Wind force to speed conversion values
- Other configuration constants

This file centralizes all constants to make maintenance easier and ensure consistency.

### `manifest.json`

Defines metadata for the integration:
- Domain name
- Name displayed in Home Assistant
- Documentation URLs
- Dependencies
- Requirements
- Version number

**Important**: When making changes to the integration, always increment the version number in this file.

### `sensor.py`

Implements sensor entities for the integration:
- Defines `SENSOR_TYPES` with all available sensors
- Implements the `JerseyWeatherSensor` class
- Sets up sensor entities with the async_setup_entry function
- Implements time-of-day aware sensors that use morning, afternoon, or evening data based on current time
- Provides future forecast periods as attributes for time-of-day aware sensors

Each sensor entity extracts specific data from the JSON response and presents it as a Home Assistant entity. Time-of-day aware sensors automatically select the appropriate data field based on the current time of day and expose future periods as attributes.

### `weather.py`

Implements the weather entity for the integration:
- Defines the `JerseyWeather` class that inherits from `WeatherEntity`
- Implements weather-specific attributes and methods
- Builds forecast data from the API response

The weather entity provides a comprehensive weather overview and forecast data.

## Version Management

### Version Numbering

The integration follows semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features, non-breaking
- PATCH: Bug fixes and minor improvements

### Updating Versions

**Important**: When making any changes to the integration, you must increment the version number in:

1. `custom_components/govje_weather/manifest.json` - The `version` field
2. `hacs.json` - The `hacs` field

Example:
```json
// manifest.json
{
  "version": "1.0.2"
}

// hacs.json
{
  "hacs": "1.0.2"
}
```

Failing to update these version numbers will prevent Home Assistant from recognizing the updated integration when installed via HACS.

## Development Workflow

1. Make code changes
2. Test locally
3. Increment version numbers in both `manifest.json` and `hacs.json`
4. Commit changes
5. Create a release (if publishing)

## Entity Naming Conventions

- All sensor entities use the naming pattern: "GOV.JE [Sensor Name]"
- The weather entity is named "GOV.JE"
- Entity unique IDs use the "govje_" prefix for consistent entity ID generation

## API Data Structure

The integration fetches data from the GOV.JE weather API at:
`https://prodgojweatherstorage.blob.core.windows.net/data/jerseyForecast.json`

Key data points include:
- Current temperature
- Wind speed and direction
- UV index
- Sunrise/sunset times
- Forecast data for multiple days

### Weather Condition Mapping

The integration uses tooltip values from the API to determine the appropriate Home Assistant weather conditions. This mapping is defined in `const.py` as `TOOLTIP_CONDITION_MAP`.

Example mappings:
```python
TOOLTIP_CONDITION_MAP = {
    "Sunny": ATTR_CONDITION_SUNNY,
    "Sunny periods": ATTR_CONDITION_PARTLYCLOUDY,
    "Cloudy with showers": ATTR_CONDITION_RAINY,
    # ...
}
```

#### Time-Specific Weather Conditions

For the current weather condition, the integration uses time-specific tooltips based on the time of day:

- Morning (5:00-11:59): Uses `iconMorningToolTip`
- Afternoon (12:00-17:59): Uses `iconAfternoonToolTip`
- Evening (18:00-4:59): Uses `iconEveningToolTip`

If a time-specific tooltip is not available, it falls back to using `dayToolTip`.

For forecast data, the integration continues to use the `dayToolTip` value for each day.

#### Adding New Tooltip Mappings

If you encounter new tooltip values that aren't mapped:

1. Identify the new tooltip value in the API response (check `dayToolTip` fields)
2. Determine the appropriate Home Assistant weather condition from the available options:
   - ATTR_CONDITION_CLEAR_NIGHT
   - ATTR_CONDITION_CLOUDY
   - ATTR_CONDITION_FOG
   - ATTR_CONDITION_HAIL
   - ATTR_CONDITION_LIGHTNING
   - ATTR_CONDITION_LIGHTNING_RAINY
   - ATTR_CONDITION_PARTLYCLOUDY
   - ATTR_CONDITION_POURING
   - ATTR_CONDITION_RAINY
   - ATTR_CONDITION_SNOWY
   - ATTR_CONDITION_SNOWY_RAINY
   - ATTR_CONDITION_SUNNY
   - ATTR_CONDITION_WINDY
   - ATTR_CONDITION_WINDY_VARIANT
3. Add the new mapping to `TOOLTIP_CONDITION_MAP` in `const.py`

Example:
```python
# Add new mapping
TOOLTIP_CONDITION_MAP["Heavy rain"] = ATTR_CONDITION_POURING
```

## API Response Structure and Quirks

### Time-of-Day Specific Fields

Many fields in the API response have time-of-day specific variants:
- Morning values: Fields with suffix `Morning` or prefix `morning` (e.g., `windspeedMphMorning`, `morningDescripiton`)
- Afternoon values: Fields with suffix `Afternoon` or prefix `afternoon` (e.g., `windspeedMphAfternoon`, `afternoonDescripiton`)
- Evening values: Fields with suffix `Evening` or prefix `night`/`evening` (e.g., `windspeedMphEvening`, `nightDescripiton`)

### Field Name Typos

Some fields in the API response have typos that must be used when accessing the data:
- Weather description fields use `Descripiton` instead of `Description` (e.g., `morningDescripiton`, `afternoonDescripiton`, `nightDescripiton`)

### Time-of-Day Logic

The integration uses the following time ranges to determine the current period:
- Morning: 5:00 - 11:59
- Afternoon: 12:00 - 17:59
- Evening: 18:00 - 4:59 (next day)

This logic is used to select the appropriate field for the current state of time-of-day aware sensors.

## Testing

To test changes:
1. Install the integration in a development Home Assistant instance
2. Verify that all entities appear with correct names
3. Check that data is updated correctly
4. Verify that forecast data is displayed properly
5. Test time-of-day aware sensors at different times of day

## Troubleshooting

Common issues:
- Entity naming issues: Check the unique_id generation in entity classes
- Data not updating: Check the coordinator update interval and API response
- Missing entities: Verify the entity setup in async_setup_entry functions
