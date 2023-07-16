# Modules Installation Guide

This guide provides instructions for configuring specific modules.

If the module you are looking for is not listed here, it is sufficient to add it in the [modules] section of the config file and set the parameters of the module section according to the Linguflex Configuration Guide. 

### [microphone_recorder] 

After linguflex successfully started you will see two buttons on the right: the wake word button and the microphone mute button.
On start both are green and enabled, meaning linguflex is listening on the microphone and waiting for a wake word to be activated.
If you disable the microphone the wake word activation will become disabled too. If you enable wake word activation, the microphone becomes enabled too. 

Linguflex starts recording in these scenarios:
1. Wake words enabled
  If wake word activation is enabled recording will start as soon as a wake word is detected
2. Wake words disabled
  If wake word activation is disabled recording will start as soon as the volume level exceeds the value defined in the volume_start_recording parameter in the [microphone_recorder] section of config.txt

Linguflex stops recording in these scenarios:
1. Wake words enabled
  - If wake word activation is enabled recording will stop as soon as a silence was detected for the time value defined in the end_of_sentence_silence_length parameter in the [microphone_recorder] section of config. The silence detection also is influenced by the parameters ema_ambient_noise_level and ema_current_noise_level.
2. Independent from wake words recording will stop when:
  - If the current volume level drops below the value defined in the volume_stop_recording parameter in the [microphone_recorder] section of config.txt
  - The microphone gets disabled in the UI

Wake words are defined in the wake_words parameter and can be one or more of the following:  alexa, americano, blueberry, bumblebee, computer, grapefruits, grasshopper, hey google, hey siri, jarvis, ok google, picovoice, porcupine, terminator. Wake word sensitivity can be set on a 0-1 scale in the wake_words_sensitivity parameter. With the tts parameter you can define the preferred text to speech output model when using the microphone (for example "azure_texttospeech").

### [personality_switch] 

Define your desired personalities within the config/personalities.de.json file. 
The starting personality is defined in config.txt under section [personality_switch] in parameter character. 
You can switch personalities at runtime by telling the system. 
If linguflex does not react to your sentence, pick a keyword and add it to config/personality_switch.en.json.
If you want to test prompts with linguflex, the config/personalities.de.json file would also be the place to go.

### [media_playout] 

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. In the search bar at the top, look for "YouTube Data API v3" and select it.
4. Click "Enable" to activate it for your project.
5. Click "Create Credentials" button on the top right.
6. Choose "User data" and click "Continue".
7. Fill in the application name and email.
8. Click "Save and Continue".
9. When asked for application type, choose "Web Application".
10. Navigate to "Credentials" on the left-side menu.
11. Click on "Create Credentials" at the top and select "API Key".

Remember to store your key either in the environment variable GOOGLE_API_KEY or in the config.txt file under the [media_playout] section with the parameter name "api_key".


