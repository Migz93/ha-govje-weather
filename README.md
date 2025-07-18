# GOV.JE Weather Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Buy me a coffee][buymecoffeebadge]][buymecoffee]

This custom integration provides weather data for Jersey (Channel Islands) from the Government of Jersey weather service.

## Features

- Weather entity with current conditions and forecast
- Multiple sensors for detailed weather information:
  - Live Current temperature
  - Daily maximum and minimum temperatures
  - Daily UV index
  - Time-of-day aware Wind speed (in mph, km/h, and knots)
  - Time-of-day aware Wind direction and force
  - Time-of-day aware Weather description
  - Time-of-day aware Rain probability
  - Time-of-day aware Forecast confidence
  - Daily Sunrise and sunset times
  - Daily Forecast summary
  
> **Note:** Time-of-day aware sensors automatically show the current period's data (morning, afternoon, or evening) as their state and include all future periods as attributes.

![example][exampleimg]

## Installation

### HACS Custom Repository (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations > Three dots in the top right > Custom repositories
   - Add `https://github.com/migz93/ha-govje-weather` with category "Integration"
3. Click "Install" on the GOV.JE Weather integration.
4. Restart Home Assistant.

### Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/migz93/ha-govje-weather).
2. Extract the contents.
3. Copy the `custom_components/govje_weather` folder to your Home Assistant's `custom_components` directory.
4. Restart Home Assistant.

## Configuration

1. Go to Settings > Devices & Services.
2. Click "Add Integration" and search for "GOVJE Weather".
3. Follow the configuration steps.

## Options

After adding the integration, you can configure the following options:

- **Refresh Interval**: How often the integration should fetch new data from the GOV.JE weather service (in minutes). The default is 10 minutes. The minimum allowed value is 5 minutes, and the maximum is 1440 minutes (24 hours).

To change these options:

1. Go to Settings > Devices & Services.
2. Find the GOV.JE Weather integration and click "Configure".
3. Adjust the refresh interval as needed.

## Data Source

The integration uses weather data from the Government of Jersey's official weather service API. The data is available at:
[https://prodgojweatherstorage.blob.core.windows.net/data/jerseyForecast.json](https://prodgojweatherstorage.blob.core.windows.net/data/jerseyForecast.json)

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

- Weather data provided by the Government of Jersey
- Integration developed by [Migz93](https://github.com/migz93)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

***

[buymecoffee]: https://www.buymeacoffee.com/Migz93
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/migz93/ha-govje-weather.svg?style=for-the-badge
[commits]: https://github.com/migz93/ha-govje-weather/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[exampleimg]: https://raw.githubusercontent.com/migz93/ha-govje-weather/main/example.png
[license]: https://github.com/migz93/ha-govje-weather/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/custom-components/integration_blueprint.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Migz93-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/migz93/ha-govje-weather.svg?style=for-the-badge
[releases]: https://github.com/migz93/ha-govje-weather/releases
[user_profile]: https://github.com/migz93
