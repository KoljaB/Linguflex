*Bringing the sci-fi dream of a capable Jarvis-style AI companion into reality.*

[![Discord](https://img.shields.io/discord/1223234851914911754)](https://discord.gg/f556hqRjpv)
[![YouTube](https://img.shields.io/youtube/channel/subscribers/UCLeuwdsZO8txzFSSAeLjGlQ?style=social&label=Subscribe%20on%20YouTube)](https://www.youtube.com/channel/UCLeuwdsZO8txzFSSAeLjGlQ)
[![Twitter](https://img.shields.io/twitter/follow/LonLigrin?style=social)](https://twitter.com/LonLigrin)

<h2>
 <img align="left" height="90px"
      src="https://github.com/KoljaB/Linguflex/assets/7604638/b4df4598-97c0-4262-807c-fa98a31dcb81"/>
      Linguflex 2.0
</h2>
<img align="right" width="30%" src="https://github.com/KoljaB/Linguflex/assets/7604638/f4fa4601-ad7c-4541-8788-b24706389197" /> 
Born out of my passion for science fiction, this project aims to simulate engaging, authentic, human-like interaction with AI personalities.  

<br>  
<br>  

It offers voice-based conversation with custom characters, alongside an array of practical features: controlling smart home devices, playing music, searching the internet, fetching emails, displaying current weather information and news, assisting in scheduling, and searching or generating images.  

I invite you to explore the framework, whether you're a user seeking an innovative AI experience or a fellow developer interested in the project. All insights, suggestions, and contributions are appreciated. I want to bring this personal passion project towards its full potential, hopefully with the community's assistance, to collectively contribute to the evolution of AI.

<br>  

> **[📓 Linguflex 2.0 installation ](./docs/installation.md)**  

<details>
<summary><strong>Understanding Installation Challenges</strong> (Click to expand)</summary>
<br>

Sometimes people suggest, "Just provide a Docker container; installation is so hard." I understand the frustration, but here's why that is challenging:

1. **Complex Integration**: Linguflex is a substantial framework combining advanced TTS technologies like realtime local neural TTS voice generation with realtime RVC fine-tuning, alongside a plethora of other features. Ensuring that all these elements work together in a single environment is like finding the lowest common denominator for your favorite 60 Python libraries instead of just three. Moreover, this system must operate consistently across various platforms, OS versions, Python environments, CUDA versions, and CuDNN versions. It's a complex puzzle.
2. **Dependency Management**: The nature of Python creates an inherently unstable environment. Even with fixed versions in requirements this does not ensure stability, as transitive dependencies - libraries our direct dependencies rely on - may update independently, potentially leading to incompatibilities or disruptions. This indirect dependency instability can introduce breaking changes over time, often requiring reinstall libraries or adjusting the dependency tree to resolve new conflicts.  


**Patience Is Key:** Please have patience with the installation process. Things might not work on the first try. Sometimes, I just need a hint to things so I can fix them, and sometimes you might be able to solve issues by yourself. While it’s rare, there are instances where there might be nothing we can do. Trying to reduce those rare cases step by step.

> **Note**: I constantly try to explore more user-friendly installation methods (and yes including docker).

</details>

> **[🎥 Installation video guide ](https://www.youtube.com/watch?v=KJ4HQ5Ud9L8)**  
> **[🎥 See in action (short clip)](https://www.youtube.com/watch?v=w5_dA5cSeLo)**  

<br> 

## Key Features

- **🆕NEW🆕:** Now featuring **Ollama** support, thanks to the exceptional **🌟[Philip Ehrbright](https://github.com/SlickTorpedo)🌟** for his incredible work in developing this feature!
- **Local Operation:** Full functionality is maintained locally, with local speech-to-text, local TTS, and local language model inference, ensuring privacy and reliability.
- **Ultra-Low Latency:** Every aspect of Linguflex was fine-tuned to minimize response times, achieving unparalleled speed in both language model communication and text-to-speech (TTS) generation.
- **High-Quality Audio:** Using voice clone technology and combining finetuned XTTS with finetuned RVC post-processing AI models, Linguflex offers a near-Elevenlabs quality in local TTS synthesis.
- **Enhanced Functionality:** Streamlined function selection allows Linguflex to quickly adapt and respond to a wide range of text-based commands and queries. We use keyword pre-parsing of user inputs to minimize the overload on the language model, making it easier to select the right functions and reducing confusion.
- **Developer-Friendly:** Building new modules is more intuitive and efficient, thanks to the minimalistic and clear coding framework.

## [Modules](./docs/modules.md)

### Core Modules
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
- **[Server](./docs/server.md):** Webserver functionality to connect external devices like smartphones etc.

### Modules Coming Soon
- **See:** Empower the assistant with visual capabilities using the GPT Vision API. Enables processing of webcam pictures and desktop screenshots.
- **Memory:** Stores and retrieves JSON-translatable data.
- **News:** Delivers compact summaries of current news.
- **Finance:** Offers financial management integrating various financial APIs for real-time tracking of investments.
- **Create:** Image generation using DALL-E API, turning text prompts into vivid images.

## Getting Started

Follow the [Modules Guide](./docs/modules.md) for step-by-step instructions about how to set up and configure the Linguflex modules.


## License

The codebase is under MIT License and the TTS model weights are under the individual TTS engine licenses listed below:

#### CoquiEngine
- **License**: Open-source only for noncommercial projects.
- **Commercial Use**: Requires a paid plan.
- **Details**: [CoquiEngine License](https://coqui.ai/cpml)

#### ElevenlabsEngine
- **License**: Open-source only for noncommercial projects.
- **Commercial Use**: Available with every paid plan.
- **Details**: [ElevenlabsEngine License](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform-)

#### AzureEngine
- **License**: Open-source only for noncommercial projects.
- **Commercial Use**: Available from the standard tier upwards.
- **Details**: [AzureEngine License](https://learn.microsoft.com/en-us/answers/questions/1192398/can-i-use-azure-text-to-speech-for-commercial-usag)

#### SystemEngine
- **License**: Mozilla Public License 2.0 and GNU Lesser General Public License (LGPL) version 3.0.
- **Commercial Use**: Allowed under this license.
- **Details**: [SystemEngine License](https://github.com/nateshmbhat/pyttsx3/blob/master/LICENSE)

#### OpenAIEngine
- **License**: please read [OpenAI Terms of Use](https://openai.com/policies/terms-of-use)
