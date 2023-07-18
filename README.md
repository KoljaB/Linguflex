# Linguflex

*A humble attempt to bring sci-fi dreams of capable Jarvis-style AI companions closer to reality, albeit in an early and not yet mature state*

## About

Born out of my passion for science fiction, this project aims to simulate engaging, authentic, human-like interaction with AI personalities.

It offers voice-based conversation with custom characters, alongside an array of practical features: controlling smart home devices, playing music, searching the internet, fetching emails, displaying current weather information and news, assisting in scheduling, and searching or generating images.

Still in its infancy, each iteration brings it a step closer to the goal. I invite you to explore the framework, whether you're a user seeking an innovative AI experience or a fellow developer interested in the project. All insights, suggestions, and contributions are appreciated. I want to bring this personal passion project towards its full potential, hopefully with the community's assistance, to collectively contribute to the evolution of AI.

## Explore Linguflex

Experience Linguflex in action in a [short video demonstration](https://www.youtube.com/watch?v=obYUkYrcAw0&t=26s), where some features are presented.

To get started, follow the steps provided in the [Installation Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/install.md) for the core software.

To tailor your assistant to your liking, take a look at the [Configuration Guide](https://github.com/KoljaB/Linguflex/blob/main/docs/config.md).

Additional modules that extend the basic functions of Linguflex can be installed using the [module installation guide](https://github.com/KoljaB/Linguflex/blob/main/docs/modules.md).

These resources are designed to make your journey with Linguflex as smooth as possible. Enjoy exploring and co-creating!

## Feature List

Linguflex offers a variety of features:

- **Conversational AI:** Natural conversations based on the OpenAI GPT-3.5-Turbo model, with the option to scale to GPT-4.

- **Modular Architecture:** Platform for easy development of your own add-on modules.

- **Multilingual:** Language files for English and German included.

- **Speech Recognition:** Speech recognition via Whisper, GPU usage with CUDA possible.

- **Custom Personalities:** Develop your own AI personalities and link them with text-to-speech voices.

- **Text-to-Speech:** Synthesis powered by ElevenLabs, Azure, Edge Browser or System voices. Supports multiple languages.

- **Smart Home Control:** Enables integration of Tuya-compatible Wi-Fi devices such as lights, plugs, and switches.

- **Media Playback:** Searches and plays music/playlists from YouTube. Includes playback controls and player UI.

- **Visual User Interface:** Intuitive graphical interface with subtle acoustic feedback on assistant actions.

- **Internet Search:** Performs text and image search using the Google Search API.

- **Memory:** Saves any data that translates to JSON format and can retrieve that information. Visual feedback in UI.

- **Emails:** Retrieves emails via IMAP

- **Scheduling Assistance:** Helps manage personal calendars and appointments. Integrates with Google Calendar.

- **Weather Updates:** Delivers current weather data and forecasts based on the user's location via OpenWeatherMap.

- **News Briefings:** Collects current news from the german "Tagesschau" news site and presents them in compact summaries.

- **Image Generation:** Creates images based on text prompts and descriptions using the DALL-E API.

- **Wake Word Activation:** Starts interactions upon detection of predefined keywords. Sensitivity can be individually adjusted.

- **Conversation History:** Retains context across conversation by managing conversation history.

- **Diagnostics:** Detailed logging for troubleshooting. Microphone calibration visualization.

- **Token-Saving Mechanisms:** Various mechanisms to save tokens, such as managing the size of the conversation history and reducing it to support both cost-effective and high-quality installations.

- **Context Sensitive Model Switching:** Automatically switches to a model with a larger context window size if needed, making it possible to scale up to the gpt-4-32k-0613 model when context size requires it.

The goal is to gradually further develop these capabilities to make the experience with the digital assistant as performant, exciting, and individual as possible.

The project is still in an early development phase, and many of the components are not mature and far from perfect.
