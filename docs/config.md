# Linguflex Configuration Guide

This guide provides instructions for configuring Linguflex through its `config.txt` file.

There is also a `config` directory with preconfigured JSON files, mainly serving to define the reactions of modules to specific keywords. You may want to edit the json files there pertaining to *text-to-speech definitions* or your *smart home setup*. 

## config.txt

This file contains:
- Essential system settings
- Module loading instructions for Linguflex server
- Module settings for:
  - Core modules (UI, OpenAI, Microphone)
  - Text-to-speech modules
  - Additional modules

### [system] 

| Parameter        | Description  |
|:-----------------|:-------------|
| language         | Language shortcut for speech-to-text conversion |
| city             | User location for weather forecast and location module |
| timezone         | Necessary for accurate time translations |
| debuglevel       | Sets logging output intensity (0-3 scale) |
| debugfunctions   | Determines function logging output detail (0-3 scale) |

### [modules] 

    user_interface
    openai_generator
    microphone_recorder
    whisper_speechtotext
    [...]

This section lists modules for Linguflex to load. Commenting out a module with a "#" prevents it from starting.

## Core module configurations

### [user_interface] 

    window_width=650
    window_height=800

These settings control the initial window size.

### [openai_generator]

| Parameter                                  | Description  |
|:-------------------------------------------|:-------------|
| api_key                                    | Your OpenAI API Key |
| default_temperature                        | Controls output randomness (0-2 scale) |
| init_prompt                                | Sets the initial OpenAI API prompt |
| gpt_model                                  | Specifies the GPT model |
| gpt_max_model                              | Specifies the maximum GPT model to use if required |
| max_history_entries                        | Limits entries kept in history |
| max_tokens_per_function                    | Caps tokens per function call |
| max_tokens_per_msg                         | Caps tokens per message |
| max_total_tokens                           | Caps total tokens in history |
| retry_attempts                             | Sets retries for failed requests |
| min_timeout                                | Minimum retry timeout in seconds |
| timeout_increase                           | Increment in retry timeout per attempt in seconds |
| estimated_processing_time_per_token        | Estimated token processing time for timeout calculation |
| output_message_token_reserve               | Reserved tokens for output message |
| security_window_for_miscalculating_tokens  | Extra tokens reserved in case of token miscalculations |
| minimum_token_window                       | Token reserve size always reserved for a function call answer |
| completion_token_reserve                   | Reserved tokens for completion |
| message_in_history_max_size_percent        | Maximum percentage of history for a single message |
| function_in_history_max_size_percent       | Maximum percentage of history for a single function call |

### [microphone_recorder]

| Parameter                         | Description  |
|:----------------------------------|:-------------|
| debug_show_volume                 | Toggle for volume level debugging |
| volume_start_recording            | Volume level to start recording |
| volume_stop_recording             | Volume level to stop recording |
| wake_words_sensitivity            | Wake word sensitivity (0-1 scale) |
| tts                               | Text-to-speech system to use (default means take the first you find) |
| wake_words                        | Words to activate system |
| ema_ambient_noise_level           | EMA factor for ambient noise calculations (0-1 scale) |
| ema_current_noise_level           | EMA factor for current noise calculations (0-1 scale) |
| end_of_sentence_silence_length    | Silence length in seconds to detect sentence end |


Please replace 'jarvis' in `wake_words` with the word you'd like to use to activate your system, the following keywords are supported: alexa, americano, blueberry, bumblebee, computer, grapefruits, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator. For other keywords than this you need to upgrade porcupine to the latest version, which then requires a permanent internet connection and a chargeable porcupine account.

### [whisper_speechtotext]

    model_size=medium

- `model_size` Defines whisper detection model

|   Size   | Parameters | English-only | Multilingual | Required VRAM | Relative speed |
|:--------:|:----------:|-------------:|-------------:|--------------:|---------------:|
| tiny     | 39 M       | tiny.en      | tiny         | ~1 GB         |  ~32x          |
| base     | 74 M       | base.en      | base         | ~1 GB         |  ~16x          |
| small    | 244 M      | small.en     | small        | ~2 GB         |  ~6x           |
| medium   | 769 M      | medium.en    | medium       | ~5 GB         |  ~2x           |
| large    | 1550 M     | N/A	         | large        | ~10 GB        |  ~1x           |

If working without CUDA you man want to choose tiny, base or small because the detection time raises with model size. With CUDA choose a model with a required VRAM that your graphics card can support. Whisper also uses the `language` parameter of the [system] section.

## Text to speech module configurations

### [system_texttospeech]

    voice=Microsoft David Desktop - English (United States)

- `voice` System voice used for text to speech

system_texttospeech module logs all available voices during linguflex startup. Pick a voice from the list in the console logging output.

### [edge_texttospeech]

| Parameter                           | Description  |
|:------------------------------------|:-------------|
| launch_wait_time_before_tts_init    | Wait time to open edge window before starting text-to-speech |
| minimize_window                     | Toggle for window minimizing after start |
| tts_wait_time_before_minimize_init  | Wait time before initializing minimize after text-to-speech starts |
| max_wait_time_for_close_windows     | Maximum wait time for window closure on shutdown |

### [azure_texttospeech]

| Parameter    | Description  |
|:-------------|:-------------|
| api_key      | Your Azure Speech API Key |
| language_tag | Standardized IETF BCP 47 language tag for Azure Speech<br>More info at [Microsoft Azure Language Support](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support) |
| region       | Azure services region |
| log_output   | Toggle for output logging |

The Azure module also uses the `language` parameter of the [system] section.

### [elevenlabs_texttospeech]

| Parameter   | Description  |
|:------------|:-------------|
| api_key     | Your ElevenLabs API Key |
| log_voices  | Whether to log the available voices or not (true or false) |

The Elevenlabs module also uses the `language` parameter of the [system] section.

## Additional module configurations

### [personality_switch]

    character=Assistant

- `character` Starting charactera as defined in config/personalities.en.json

### [google_information]

| Parameter   | Description  |
|:------------|:-------------|
| api_key     | [Google Cloud API key](https://console.cloud.google.com/) with clearance for the Custom Search API<br>Only needed here if not already defined in environment variable GOOGLE_API_KEY |
| cse_id      | [Google search engine ID}(https://cse.google.com/cse/all) (cx id) if not already defined in GOOGLE_CSE_ID |

### [media_playout]

| Parameter   | Description  |
|:------------|:-------------|
| api_key     | [Google Cloud API key](https://console.cloud.google.com/) with clearance for the YouTube Data API (v3)<br>Only needed here if not already defined in environment variable GOOGLE_API_KEY |

### [weather_forecast]

| Parameter   | Description  |
|:------------|:-------------|
| api_key     | [OpenWeatherMap API Key](https://openweathermap.org/api) |

### [email_imap]

| Parameter    | Description  |
|:-------------|:-------------|
| server       | Your IMAP email server (e.g., imap.web.de) |
| username     | Your email login username |
| password     | Your email password |
| history_days | Number of days to look into email history |

### [picture_search]

| Parameter   | Description  |
|:------------|:-------------|
| api_key     | [Google Cloud API key](https://console.cloud.google.com/) with clearance for the Custom Search API<br>Only needed here if not already defined in environment variable GOOGLE_API_KEY |
| cse_id      | [Google search engine ID}(https://cse.google.com/cse/all) (cx id) if not already defined in GOOGLE_CSE_ID |

### [play_sound]

| Parameter   | Description  |
|:------------|:-------------|
| notice_message_seconds | Time in seconds after which a notice sound is played out (set to 0 to disable) |

### [wled]

| Parameter   | Description  |
|:------------|:-------------|
| wled_url | Url to connect to wled digital RGB LEDs with an ESP8266 or ESP32 |

### [stocks_portfolio]

| Parameter   | Description  |
|:------------|:-------------|
| summary_url | Single url to a comdirect "Musterdepot" which will get parsed in as the depot summary |
| depot_names | List of comma-separated names for the following depot urls |
| depot_urls  | List of comma-separated depot urls containing comdirect Musterdepots to retrieve detailled information from |

Currently stock portfolio module relies on a comdirect Musterportfolio to parse in investment data. I am aware of this very specific solution and that only few people can use it in the way it's implemented currently. A more general solution is in work. 
