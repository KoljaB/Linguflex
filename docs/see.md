# See/Vision Module for Linguflex

The See/Vision module for Linguflex enables the AI assistant to capture and process images from the webcam and screen, providing visual context to its interactions.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Limitations](#limitations)

## Functionality

This module offers two main functionalities:

1. **Webcam Capture**: Allows the AI to capture an image from the webcam.
2. **Screen Capture**: Enables the AI to take a screenshot of the entire desktop.

Both captured images can be processed and analyzed by the AI to provide context-aware responses.

## Examples

- "What are you seeing right now?"
- "Look at the webcam now."
- "Show what the webcam sees."
- "Look at the desktop."
- "What can you see on my PC?"
- "Look what's going on at my PC."

## Installation

The See/Vision module is included in the Linguflex package.

## Configuration

### settings.yaml

**Section:** see

- `model`: The model to use for image processing. Currently set to "gpt-4o".
- `img_width`: Width of the captured image. Default is 1024.
- `img_height`: Height of the captured image. Default is 768.
- `output_file_webcam`: File path for saving webcam images. Default is "webcam.jpg".
- `output_file_screenshot`: File path for saving screen captures. Default is "screen.jpg".
- `max_tokens`: Maximum number of tokens for the AI response. Default is 1000.

Example configuration:

```yaml
see:
  model: gpt-4o
  img_width: 1024
  img_height: 768
  output_file_webcam: webcam.jpg
  output_file_screenshot: screen.jpg
  max_tokens: 1000
```

## Limitations

- The module currently only works when GPT-4o is used as both the language model and vision module.
- Webcam functionality requires a compatible webcam connected to the system.
- Screen capture functionality may be affected by system permissions and multi-monitor setups.

## Contributing

If you encounter any issues or have suggestions for improvements, please open an issue on the Linguflex GitHub repository or contribute to the project through pull requests.
