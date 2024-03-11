# Weather Module for Linguflex

The Weather module for Linguflex provides weather forecasts using the OpenWeather API.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)

## Functionality

The Weather module retrieves weather information from the OpenWeather API for a specified city. Users can inquire about current weather conditions or forecasts for different time intervals in a pre-defined city or any other specified location.

## Examples

- "Is it raining in the evening?"
- "What's the weather like tomorrow in San Francisco?"

## Installation

### Environment Variables

`OPENWEATHERMAP_API_KEY`

This module requires an OpenWeather API Key set as the environment variable `OPENWEATHERMAP_API_KEY`.

To obtain an API key:

1. Sign up for an account at [OpenWeatherMap](https://home.openweathermap.org/users/sign_up).
2. Navigate to "My API keys" from the drop-down menu on the top right.
3. Copy the displayed API key to your clipboard.
4. Store the key in the `OPENWEATHERMAP_API_KEY` environment variable (consult specific instructions for your operating system).

## Configuration

### Settings.yaml

**Section:** weather

- `city`: The default city for retrieving the weather forecast.

