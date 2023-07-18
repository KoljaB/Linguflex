# Linguflex

*A humble attempt to bring sci-fi dreams of capable Jarvis-style AI companions closer to reality, albeit in an early and imperfect state*

## About 

Born out of a fascination for science fiction, this project aims to simulate engaging, human-like interaction within a digital framework.

It offers voice-based conversation with custom AI personalities, alongside an array of practical features: it can control smart home devices, play music, conduct Internet searches, retrieve emails, present weather updates and news, assist with scheduling appointments, and perform image search and generation.

Currently in its early stage, each iteration brings it a step closer to the goal. As the sole developer, I'm dedicated to refining its capabilities and broadening its features.

I invite you to explore the framework, whether you're a user seeking an innovative AI experience or a fellow developer interested in the project. All insights, suggestions, and contributions are appreciated. My hope is that, with the community's assistance, we can bring this personal passion project towards its full potential, collectively contributing to the evolution of AI.

## Exploring Further

See it in action in this [short video demonstration](https://www.youtube.com/watch?v=obYUkYrcAw0&t=26s) highlighting some of its functionality.

To get started, follow the steps provided in the [Installation Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/install.md) for the core software.

To configure your assistant to your liking, consult the [Configuration Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/config.md).

For extending core functionality by installing modules, please get more detailed insights by referring to the [Modules Installation Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/modules.md).

These resources are designed to make your journey with Linguflex as smooth as possible. Enjoy exploring and co-creating!

## Feature List

The app provides a wide range of capabilities to deliver a fully-featured digital assistant experience:

- **Conversational AI:** Natural language conversations powered by OpenAI's GPT-3.5-Turbo model with support to scale up to GPT-4. 

- **Modular Architecture:** Operates on a modular framework which allows for the development of personalized skills through Python assistant modules.

- **Multilingual Support:** Conversations in multiple languages supported. English and german language files are included.

- **Voice Interactions:** Speech recognition via Whisper, also allowing GPU utilization with CUDA.

- **Custom Personalities:** Users have the ability to develop their own custom personalities and link them with specific text-to-speech voices.

- **Text-to-Speech:** Synthesis powered by ElevenLabs, Azure, Edge Browser or System voices. Supports multiple languages.

- **Smart Home Control:** Integrates with Tuya-compatible WiFi devices like lights, plugs and switches via the local API.

- **Media Playback:** Searches and plays music/playlists from YouTube. Includes playback controls and player UI.

- **Visual User Interface:** Intuitive graphical interface with subtle acoustic feedback on assistant actions.

- **Internet Search:** Performs text and image search using the Google Search API.

- **Memory:** Saves any data that translates to JSON format and can retrieve that information. Visual feedback in UI.

- **Emails:** Retrieves emails via IMAP

- **Scheduling Assistance:** Helps manage personal calendars and appointments. Integrates with Google Calendar.

- **Weather Updates:** Provides current weather and forecasts based on the user's location via OpenWeatherMap.

- **News Briefings:** Summarizes top news scraped from the german "Tagesschau" news site.

- **Image Generation:** Creates images based on text prompts and descriptions via DALL-E API.

- **Wake Word Activation:** Starts interaction on detecting preset wake words. Custom sensitivity tuning.

- **Conversation Flow:** Maintains context over multi-turn conversations using history tracking.

- **Diagnostics:** Detailed logging for troubleshooting. Microphone calibration visualization.

- **Token-Saving Mechanisms:** Various token-saving mechanisms, such as custom history size management and reduction, accommodating both low-budget and high-end installations.

- **Context Sensitive Model Switching:** Automatically switches to a model with a larger context window size if needed, making it possible to scale up to the gpt-4-32k-0613 model when context size requires it.


The goal is to incrementally evolve those capabilities to deliver an engaging, personalized and helpful digital assistant experience. Remember this project is in an early development stage and lots of components are still imperfect.
