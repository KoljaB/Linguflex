# Home Assistant Module for Linguflex

The Home Assistant module for Linguflex interacts with your Home Assistant server, allowing for access to your smart home ecosystem.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Configuration](#configuration)

## Functionality

The Home Assistant module performs several key functions:

- Retrieves the states of entities from Home Assistant.
- Allows control over lights, including turning them on/off and setting their color.
- Filters entities based on specified whitelist and blacklist criteria.
- Extracts and processes relevant attributes for specific entity types.
- Manages locks, including locking and unlocking doors.
- Sets the temperature on climate control devices.
- Retrieves various system configurations and settings.
- Provides access to calendar events.
- Retrieves the history and logbook entries of specific devices.
- Fires custom events in the Home Assistant system.

## Examples

- "Get the current state of all lights in the house."
- "Turn on the living room light."
- "Set the kitchen light to blue."
- "Provide a summary of all sensors in the home."
- "Can you check the status of my smart home devices?"
- "Can you turn the light at the altar on?"
- "Make the lower couch lamp shine in a nice mellow orange way."
- "I want the bulb for the pc to be switched off."
- "Can you set the living room temperature to 22 degrees?"
- "Adjust the temperature in the bedroom to 20 degrees."
- "Can you lock the front door?"
- "Secure the back door."
- "I want to unlock the garage door."
- "Can you show me the current configuration of my Home Assistant system?"
- "Show me the recent activities in my smart home system."
- "I want to see the events in my home automation system."
- "Show me the available actions in my smart home system."
- "Retrieve the history of my bedroom thermostat for the past week."
- "I want to see the history of the kitchen door lock for the past month."
- "Can you show me the logbook entries for the living room light for the past day?"
- "Retrieve the calendars from my smart home system."
- "Can you show me the events from my personal calendar for the past day?"
- "Can you update the state of the living room light to on?"
- "Initiate the alarm_triggered event in my smart home system."
- "I want to fire the motion_detected event in my home automation system."

## Configuration

### Settings.yaml

**Section:** home_assistant

- `home_assistant_url`: The URL or IP address of your local Home Assistant server (e.g., `homeassistant.local` or `192.168.1.XXX`).
- `bearer_token`: The bearer token used for authenticating with your Home Assistant instance.
- `entity_whitelist`: A list of entity types or specific entities to include (e.g., `switch.,light.,sensor.,person.,weather.`).
- `entity_blacklist`: A list of entity identifiers to exclude (e.g., `_kindersicherung,_parental`).
- `attribute_map`: A mapping of entity types to the attributes that should be extracted and processed (e.g., `light` attributes like `brightness`, `color_mode`, etc.).

### Example Configuration

```yaml
home_assistant:
  home_assistant_url: homeassistant.local # replace by your local home assistant server IP (e.g. 192.168.178.XXX)
  bearer_token: replace_this_by_your_home_assistant_bearer_token
  entity_whitelist: switch.,light.,sensor.,person.,weather.
  entity_blacklist: _kindersicherung,_parental
  attribute_map:
    light:
      - brightness
      - color_mode
      - supported_color_modes
      - color_temp
      - hs_color
    switch: []
```
