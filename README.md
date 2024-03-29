# Linguflex 2.0

*Bringing the sci-fi dream of a Jarvis-style AI companion into reality. Presenting Linguflex 2.0 – an evolving journey towards an advanced AI assistant.*

[![Discord](https://img.shields.io/discord/1223234851914911754)](https://discord.gg/f556hqRjpv)
[![YouTube](https://img.shields.io/youtube/channel/subscribers/UCLeuwdsZO8txzFSSAeLjGlQ?style=social&label=Subscribe%20on%20YouTube)](https://www.youtube.com/channel/UCLeuwdsZO8txzFSSAeLjGlQ)
![Twitter](https://img.shields.io/twitter/follow/LonLigrin?style=social)

> **[📓 Linguflex 2.0 installation ](./docs/installation.md)**  
> **[🎥 Video guide ](https://www.youtube.com/watch?v=KJ4HQ5Ud9L8)**  


## Introduction

Linguflex 2.0 emerges from a deep-rooted passion for science fiction, aspiring to create voice-based, dynamic, and convincingly human-like interactions with AI. Linguflex is a solid voice based function calling framework supporting a variety of LLMs (local included). It combines relentless pursuit of minimal latency (ensuring rapid responses) with a outstanding TTS voice quality, all locally generated. This new version marks a significant stride towards realizing a versatile, yet specialized AI assistant.

## Key Advancements in 2.0

### Performance Focus
- **Ultra-Low Latency:** Every aspect of Linguflex was fine-tuned to minimize response times, achieving unparalleled speed in both language model communication and text-to-speech (TTS) generation.
- **Local Operation:** Full functionality is maintained locally, encompassing speech-to-text, TTS, and language model inference, ensuring privacy and reliability.
- **High-Quality Audio:** Integrating advanced voice clone technology for real-time post-processing, Linguflex offers a near-Elevenlabs quality in local TTS synthesis.
- **Enhanced Functionality:** Streamlined function selection allows Linguflex to quickly adapt and respond to a wide range of text-based commands and queries.
- **Developer-Friendly:** Building new modules is more intuitive and efficient, thanks to the minimalistic and clear coding framework.

## [Modules](./docs/modules.md)

### Core Features
- **Listen (Audio Input Module):** Serving as Linguflex's auditory system, this module captures spoken instructions via the microphone with precision.
- **[Brain](./docs/brain.md):** Cognitive Processing Module. Heart of Linguflex, processes user input, either with a local language model or OpenAI GPT API.
- **Speech (Audio Output Module):** Offers realtime TTS with various provider options, and advanced voice tuning capabilities, including Realtime Voice Cloning (RVC).

### Current Expansion Modules
- **[Mimic](./docs/mimic.md):** This creative tool allows users to design custom AI characters, assign unique voices created with the Speech module, and switch between them.
- **[Music](./docs/music.md):** A voice-command module for playing selected songs or albums, enhancing the user experience with musical integration.
- **[Mail](./docs/mail.md):** Retrieves emails via IMAP, integrating with your digital correspondence.
- **[Weather](./docs/weather.md):** Provides current weather data and forecasts, adapting to your location.
- **[House](./docs/house.md):** Smart Home control for Tuya-compatible devices, enhancing your living experience.
- **[Calendar](./docs/calendar.md):** Manages personal calendars and appointments, including Google Calendar integration.
- **[Search](./docs/search.md):** Performs text and image searches using the Google Search API.

### Modules Coming Soon
- **See:** Empower the assistant with visual capabilities using the GPT Vision API. Enables processing of webcam pictures and desktop screenshots.
- **Memory:** Stores and retrieves JSON-translatable data.
- **News:** Delivers compact summaries of current news.
- **Finance:** Offers financial management integrating various financial APIs for real-time tracking of investments.
- **Create:** Image generation using DALL-E API, turning text prompts into vivid images.

## Getting Started

Follow the [Modules Guide](./docs/modules.md) for step-by-step instructions about how to set up and configure the Linguflex modules.
