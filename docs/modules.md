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
2. Create a new project or open your existing one.
3. In the search bar at the top type "Youtube API", look for "YouTube Data API v3" and select it.
4. Click "Enable" to activate it for your project.
5. Click "Create Credentials" button on the top right.
6. Choose "User data" and click "Continue".
7. Fill in the application name and email.
8. Click "Save and Continue".
9. When asked for application type, choose "Web Application".
10. Navigate to "Credentials" on the left-side menu.
11. Click on "Create Credentials" at the top and select "API Key".

The key is then stored either in the environment variable GOOGLE_API_KEY (in start_linguflex.bat) or in the config.txt file under the [media_playout] section with the parameter name "api_key".

### [email_imap] 

1. Identify your email provider's IMAP server: If you don't know it, you can often find it with a quick internet search. For example, you might search "IMAP server for Gmail" or "IMAP server for Yahoo Mail".
2. Know your email username and password: These are the credentials you use to log into your email account.
3. Decide on the number of days of email history you want to access: The "history_days" parameter lets you set how much of your email history to download or synchronize.
4. Open the config.txt in a text editor, search for the section [email_imap] and replace the placeholder values with your actual details.

Be careful not to share this file or expose it publicly, as it contains sensitive information.

### [weather_forecast] 

1. Create a [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) account.
2. From the drop down menu on the top right select "My API keys"
3. Copy the key that is displayed now into your clipboard
4. Open the config.txt in a text editor, search for the section [weather_forecast] and paste the key under api_key OR store the key in the environment variable OPENWEATHERMAP_API_KEY (for example open the start_linguflex.bat and paste the key under OPENWEATHERMAP_API_KEY)

### [google_information] 

#### Get google api key

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or open your existing one.
3. In the search bar at the top type "Custom search", look for "Custom Search API" and select it.
4. Click "Enable" to activate it for your project.
5. Click "Create Credentials" button on the top right.
6. Choose "User data" and click "Continue".
7. Fill in the application name and email.
8. Click "Save and Continue".
9. When asked for application type, choose "Web Application".
10. Navigate to "Credentials" on the left-side menu.
11. Click on "Create Credentials" at the top and select "API Key".

The key is then stored either in the environment variable GOOGLE_API_KEY (for example in start_linguflex.bat) or in the config.txt file under the [google_information] section with the parameter name "api_key".

#### Get google search engine ID

1. Go to Googles [Search Engine Site](https://cse.google.com/cse/all).
2. Click "create search engine"
3. Give a name for the engine and select "Search the entire web"
4. After that process there will be a page with a field named "Search engine ID" 

This ID is then stored either in the environment variable GOOGLE_CSE_ID (for example in start_linguflex.bat) or in the config.txt file under the [google_information] section with the parameter name "cse_id".
