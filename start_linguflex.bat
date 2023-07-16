@echo off

:: switch to current execution directory
cd /d %~dp0


:: setup environment
::────────────────────────────────────

:: OpenAI API Key  https://platform.openai.com/
:: - essential to run linguflex
set OPENAI_API_KEY=

:: Microsoft Azure API Key  https://portal.azure.com/
:: - optional [azure_texttospeech]
set AZURE_SPEECH_KEY=

:: Elevenlabs API Key  https://beta.elevenlabs.io/Elevenlabs
:: - optional [elevenlabs_texttospeech]
set ELEVENLABS_SPEECH_KEY=

::  Google Cloud API key  https://console.cloud.google.com/
:: - optional [media_playout] (API key needs access to the YouTube Data API v3)
:: - optional [picture_search] (API key needs access to the Custom Search API)
set GOOGLE_API_KEY=

::  Search engine ID / Suchmaschinen-ID  https://cse.google.com/cse/all
:: - optional [picture_search]
set GOOGLE_CSE_ID=

::  Serp API key  https://serpapi.com/
:: - optional [google_information]
set SERP_API_KEY=

::   OpenWeatherMap API Key  https://openweathermap.org/api
:: - optional [weather_forecast]
set OPENWEATHERMAP_API_KEY=

:: Check if OPENAI_API_KEY is set
if not defined OPENAI_API_KEY (
    echo OPENAI_API_KEY environment variable is not set. 
    echo OpenAI API Key therefore expected in config.txt[openai_generator][api_key].
)

:: start linguflex
::────────────────────────────────────

TITLE LinguFlex
python linguflex.py
pause
cmd