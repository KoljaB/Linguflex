# Linguflex
Linguflex is a **personal AI assistant** ("Jarvis") that **responds to spoken word**.

## Key Features
Linguflex can:

- Mimic **personalities** 🎭
- Play **music** 🎵
- Manage **appointments** 📆
- Retrieve **emails** 📧
- Announce the **weather** ☀️🌦️
- Present **news** 📰
- **Search the Internet** (texts or images) 🔍
- **Generate images** 🎨
- **Control lamps** 💡
- Keep an eye on your stock portfolio 📊

Linguflex is available in English and German ([zur deutschen Readme-Datei](https://github.com/KoljaB/Linguflex/blob/main/README_DE.md)).  

Watch some of the features: 

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/BzAOBQUVMK0/0.jpg)](https://www.youtube.com/watch?v=BzAOBQUVMK0)

## Prerequisites
- [Python 3.9.9](https://www.python.org/downloads/release/python-399/)
- [OpenAI API Key](https://platform.openai.com/) 

## Installation

[Comprehensive Installation Guide](https://github.com/KoljaB/Linguflex/blob/main/INSTALL.md)

```
pip install -r requirements.txt
```
or for a minimal configuration ("Vanilla"): `pip install -r requirements_minimal.txt`

Enter OpenAI API key either:
- into the file `config.txt` in the section [openai_generator] into the key "api_key"
- or into the environment variable OPENAI_API_KEY

Note: For faster speech recognition with GPU support, the [NVIDIA® CUDA® Toolkit](https://developer.nvidia.com/cuda-toolkit) should be installed before the (pytorch-)installation.

## Start
```
python linguflex
```

## Configuration
The `config.txt` includes:
- System settings such as the languages used
- the modules to be loaded in the [modules] section (modules are loaded and started in the order specified here)
- the configuration parameters of the modules

---

# Basic Modules

```
user_interface
openai_generator
microphone_recorder
whisper_speechtotext
system_texttospeech
```

Enable basic voice communication with the assistant. 

## Microphone Calibration
First, the microphone should be set in the section [microphone_recorder] of the configuration file config.txt. Recording begins when the level exceeds the value in `volume_start_recording` and stops when the level falls below the value in `volume_stop_recording`. To determine these values, set debug_show_volume = True and start Linguflex, the exact level values are then written to the console window.

---

# Text-to-Speech Modules

These modules provide enhanced speech output and replace the existing `system_texttospeech` module in the `[modules]` section of the configuration file.

The modules for Azure and Elevenlabs can be operated in parallel and need API keys, which are stored in the respective section in the configuration file or defined as an environment variable. Localized voices are managed for these two modules in their respective voice configuration file.

  - `edge_texttospeech` uses the Edge browser window for speech output, provides free, high-quality speech synthesis, but with slightly reduced stability and comfort due to the use of the browser window.
  - `azure_texttospeech` provides high-quality, stable and comfortable speech synthesis; requires a [Microsoft Azure API Key](https://portal.azure.com/); enter api key in section azure_texttospeech into the key api_key or in the registry environment variable AZURE_SPEECH_KEY; voice configuration file: azure_texttospeech.voices.de/en.json
  - `elevenlabs_texttospeech` also offers high-quality, stable and comfortable speech synthesis with emotional output; requires an [Elevenlabs API Key](https://beta.elevenlabs.io/Elevenlabs); enter api key in section elevenlabs_texttospeech into the key api_key or in the registry environment variable ELEVENLABS_SPEECH; voice configuration file: elevenlabs_texttospeech.voices.de/en.json

---

# Extension Modules

## Mimic Personalities 🎭
`personality_switch`
- Function: Switches to the specified personality.
- Note: The starting personality can be specified in the configuration under "character". Available personalities are managed in the personality_switch.de/en.json file in modules/basic.

  **Examples:**
  - *"Transform into Bruce Willis"*
  - *"Be Mickey Mouse"*
  - *"Change character to Assistant"*

## Notebook 📔
`notebook`
- Function: Can be used as a clipboard for information.

  **Examples:**
  - *"Write the URL of the current song into the notebook"*
  - *"Create a notebook Animals and write Cat, Mouse and Elephant into it"*

## Media Playout 🎵
`media_playout`
- Function: Allows search and playback of music tracks and music playlists. In playlists, a song can be skipped forward and backward.
- Note: Requires a [Google Cloud API key](https://console.cloud.google.com/) with access to the YouTube Data API v3 in config.txt (section media_playout, key api_key) or environment variable GOOGLE_API_KEY. 

  **Examples:**
  - *"Play a playlist by Robbie Williams"*
  - *"Next song"*
  - *"Quieter", "Stop", "Pause", "Continue"*

## Internet Search Text 🔍 
`google_information`
- Function: Retrieves real-time information from the Internet.
- Note: Requires a [SerpAPI Key](https://serpapi.com/) in config.txt (section google_information, key api_key) or environment variable SERP_API_KEY. 

  **Example:**
  - *"Google, who was the 2023 football champion?"*

## Auto Action ✨
`auto_action`
- Function: Allows the assistant to access the abilities of all modules for difficult questions.

  **Example:**
  - *"Who was the 2023 football champion?"*

## Manage Appointments 📆
`google_calendar`
- Function: Integrates the Google Calendar to retrieve and add events.
- Note: Requires the [credentials.json](https://developers.google.com/calendar/api/quickstart/python?hl=de#authorize_credentials_for_a_desktop_application) file. Put the file into linguflex execution directory.

  **Examples:**
  - *"What appointments do I have?"*
  - *"New appointment the day after tomorrow at 9 am dentist"*
  - *"Postpone the dinner appointment by one hour"*

## Weather ☀️🌦️
`weather_forecast`
- Function: Retrieves current weather data.
- Note: Requires an [OpenWeatherMap API Key](https://openweathermap.org/api) in config.txt (section weather_forecast, key api_key) or environment variable OPENWEATHERMAP_API_KEY. 

  **Example:**
  - *"What's the weather like tomorrow morning?"*

## News 📰
`news_summary`
- Function: Summarizes the current news of Tagesschau.

  **Example:**
  - *"What's the tech news?"*

## Picture Search 🔍🖼️
`picture_search`
- Function: Searches the Internet for a picture and displays it.
- Note: Requires a [Google API Key](https://console.cloud.google.com) (section picture_search, key api_key) with clearance for the Custom Search API and a [CX Key](https://cse.google.com/cse/all) in config.txt (section picture_search, key cx_key) or environment variables GOOGLE_API_KEY and GOOGLE_CX_KEY. 

  **Example:**
  - *"Show a picture of Salvador Dali"*

## Image Generation 🎨
`picture_generator`
- Function: Generates an image based on a description and displays it.
- Note: Intense use can [incur costs](https://openai.com/pricing).

  **Example:**
  - *"Paint a picture of the Eiffel Tower in the style of Salvador Dali"*

## Email Access  📧
`email_imap`
- Function: Retrieves emails using the IMAP protocol.

  **Example:**
  - *"Do I have new emails?"*

## Investment Data 📊  
`stocks_portfolio`
- Function: Retrieves investment portfolio data and summarizes it.
- Note: Portfolio links are written in config.txt as "comdirect Musterportfolio".

  **Example:**
  - *"How are my stocks doing"*
