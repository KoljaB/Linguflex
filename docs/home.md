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

## Examples

- "Get the current state of all lights in the house."
- "Turn on the living room light."
- "Set the kitchen light to blue."
- "Provide a summary of all sensors in the home."

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
