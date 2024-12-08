# Music Module for Linguflex

The Music module for Linguflex allows for the playout of songs and albums via YouTube.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)

## Functionality

This module facilitates:

- Playing individual songs or entire albums using YouTube links.
- Accessing a variety of music through YouTube's extensive library.

## Examples

- "Play an album by Adele."
- "Play 'Bohemian Rhapsody' by Queen."
- "I wanna hear a playlist of the top songs from the 90s."

## Installation

### VLC Player

Please install VLC player. The [Python VLC library](https://github.com/videolan/vlc) depends on it to stream and play music from YouTube. Linguflex requires VLC to be installed for its music module player to work correctly.

### Environment Variables

`GOOGLE_API_KEY`

This module requires a Google API Credentials Key with YouTube Data API v3 enabled, set as the environment variable `GOOGLE_API_KEY`.

To obtain this key:

1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Search for "YouTube Data API v3" and enable it.
4. Click "Create Credentials" and choose "User data".
5. Provide the necessary application details.
6. For application type, select "Web Application".
7. Find "Credentials" in the menu, then create an "API Key".
8. Store this key in the `GOOGLE_API_KEY` environment variable (refer to your OS for instructions).

## Configuration

### Settings.yaml

**Section:** music

- `max_playlist_songs`: Defines the maximum number of songs in a playlist to be retrieved using the YouTube API.

