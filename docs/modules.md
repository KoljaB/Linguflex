# Modules Installation Guide

This guide provides instructions for configuring specific modules.

If the module you are looking for is not listed here, it is sufficient to add it in the [modules] section of the config file and set the parameters of the module section according to the Linguflex Configuration Guide. 

## [microphone_recorder] 

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

## [personality_switch] 

Define your desired personalities within the config/personalities.de.json file. 
The starting personality is defined in config.txt under section [personality_switch] in parameter character. 
You can switch personalities at runtime by telling the system. 
If linguflex does not react to your sentence, pick a keyword and add it to config/personality_switch.en.json.
If you want to test prompts with linguflex, the config/personalities.de.json file would also be the place to go.

## [media_playout] 

1. Go to [Google Cloud Console](https://console.cloud.google.com/).

2. Create a new project or open your existing one.

3. In the search bar at the top type "Youtube API", look for "YouTube Data API v3" and select it.

4. Click "Enable" to activate it for your project.

5. Click "Create Credentials" button on the top right.

6. Choose "User data" and click "Continue".

7. Fill in the application name and email, then click "Save and Continue".

8. When asked for application type, choose "Web Application".

9. Navigate to "Credentials" on the left-side menu.

10. Click on "Create Credentials" at the top and select "API Key".

The key is then stored either in the environment variable GOOGLE_API_KEY (in start_linguflex.bat) or in the config.txt file under the [media_playout] section with the parameter name "api_key".

## [email_imap] 

1. Identify your email provider's IMAP server: If you don't know it, you can often find it with a quick internet search. For example, you might search "IMAP server for Gmail" or "IMAP server for Yahoo Mail".

2. Know your email username and password: These are the credentials you use to log into your email account.

3. Decide on the number of days of email history you want to access: The "history_days" parameter lets you set how much of your email history to download or synchronize.

4. Open the config.txt in a text editor, search for the section [email_imap] and replace the placeholder values with your actual details.

Be careful not to share this file or expose it publicly, as it contains sensitive information.

## [weather_forecast] 

1. Create a [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) account.

2. From the drop down menu on the top right select "My API keys"

3. Copy the key that is displayed now into your clipboard

4. Open the config.txt in a text editor, search for the section [weather_forecast] and paste the key under api_key OR store the key in the environment variable OPENWEATHERMAP_API_KEY (for example open the start_linguflex.bat and paste the key under OPENWEATHERMAP_API_KEY)

## [google_information] 

### Get google api key

1. Go to [Google Cloud Console](https://console.cloud.google.com/).

2. Create a new project or open your existing one.

3. In the search bar at the top type "Custom search", look for "Custom Search API" and select it.

4. Click "Enable" to activate it for your project.

5. Click "Create Credentials" button on the top right.

6. Choose "User data" and click "Continue".

7. Fill in the application name and email then click "Save and Continue".

8. When asked for application type, choose "Web Application".

9. Navigate to "Credentials" on the left-side menu.

10. Click on "Create Credentials" at the top and select "API Key".

The key is then stored either in the environment variable GOOGLE_API_KEY (for example in start_linguflex.bat) or in the config.txt file under the [google_information] section with the parameter name "api_key".

### Get google search engine ID

1. Go to Googles [Search Engine Site](https://cse.google.com/cse/all).

2. Click "create search engine"

3. Give a name for the engine and select "Search the entire web"

4. After that process there will be a page with a field named "Search engine ID" 

This ID is then stored either in the environment variable GOOGLE_CSE_ID (for example in start_linguflex.bat) or in the config.txt file under the [google_information] section with the parameter name "cse_id".

## [google_calendar] 

To access the Google Calendar API with linguflex, you will need to follow these steps to obtain the `credentials.json` file:

1. Go to the [Google Developers Console](https://console.developers.google.com/).

2. Create a new project or select an existing project from the top dropdown menu.

3. Enable the Google Calendar API:
   - Click on the "Enable APIs and Services" button.
   - Search for "Google Calendar API" and select it.
   - Click on the "Enable" button.

4. Create credentials for your project:
   - In the left sidebar, click on "Credentials."
   - Click on the "Create credentials" button and select "OAuth client ID."
   - Configure the OAuth consent screen by providing a name and email address.
   - Select "Desktop app" as the application type.
   - Click on the "Create" button.

5. Download the credentials:
   - After creating the credentials, a dialog box will appear displaying your client ID and client secret.
   - Click on the "Download JSON" button next to your client ID to download the `credentials.json` file.
   - Save the file in a secure location on your computer.

Once you have the `credentials.json` file, store that file in the executing directory of linguflex.

## [picture_search]

### Get google api key 

The same keys are needed as in [google_information]:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).

2. Create a new project or open your existing one.

3. In the search bar at the top type "Custom search", look for "Custom Search API" and select it.

4. Click "Enable" to activate it for your project.

5. Click "Create Credentials" button on the top right.

6. Choose "User data" and click "Continue".

7. Fill in the application name and email then click "Save and Continue".

8. When asked for application type, choose "Web Application".

9. Navigate to "Credentials" on the left-side menu.

10. Click on "Create Credentials" at the top and select "API Key".

The key is then stored either in the environment variable GOOGLE_API_KEY (for example in start_linguflex.bat) or in the config.txt file under the [picture_search] section with the parameter name "api_key".

### Get google search engine ID

1. Go to Googles [Search Engine Site](https://cse.google.com/cse/all).

2. Click "create search engine"

3. Give a name for the engine and select "Search the entire web"

4. After that process there will be a page with a field named "Search engine ID" 

This ID is then stored either in the environment variable GOOGLE_CSE_ID (for example in start_linguflex.bat) or in the config.txt file under the [picture_search] section with the parameter name "cse_id".

## [smart_home_devices]

Controls tuya devices like smart bulbs, smart plugs or smart switches.  
To access the smart devices over the local network (without using the cloud/internet) we need to give linguflex specific information about the devices. To get these we can follow these steps:

### Connect devices to tuya cloud

Connect your devices with your tuya app (smart-life app or comparable). Then follow these steps:

1. Create a [Tuya Account](https://iot.tuya.com/) and log in.

2. Create a cloud project, give a name and select "smart home" under industry and development method and select the data center for your region.

3. Add the Device Status Notification API to the project

4. After creating the project the next page should be "Overview" Tab from the "Cloud" menu. Remember Access ID/Client ID and Access Secret/Client Secret.

5. From the tab bar where also "Overview" is located click on the right on "Devices"

6. On the bar one line below that click "Link Tuya App Account", then click "Add App Account"

7. Scan the displayed QR Code with your Tuya Application (Smart-Life App etc, there are many; the option for that is often under "profile" and sometimes a button on the top)

8. Change the permissions to "Read, write and Manage"

9. Now the devices will show up in the Tuya cloud.

### Read device parameters from cloud

1. Open a console and run
```bash
   python -m tinytuya
   ```

2. Copy the output of the console into a text editor. 

3. Then run

   ```bash
   python -m tinytuya wizard
   ```

4. When asked "Enter API Key from tuya.com" enter the Access ID/Client ID from point 4. of the "Connect devices to tuya cloud" section

5. When asked "Enter API Secret from tuya.com" enter the Access Secret/Client Secret from point 4. of the "Connect devices to tuya cloud" section 

6. When asked "Enter any Device ID" enter "scan"

7. Enter region of tuya cloud project

8. Copy the output of the console into a text editor. 

9. Search in the output for the values "id", "key", "version" and the ip adress of the devices you want to add from the output. 

10. Store these values into config/smart_home_devices.json
