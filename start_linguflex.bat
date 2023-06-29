@echo off

:: switch to current execution directory
cd /d %~dp0


:: setup environment
::────────────────────────────────────

:: OpenAI API Key  https://platform.openai.com/
:: - essential to run linguflex
set LINGU_OPENAI_API_KEY=

:: Microsoft Azure API Key  https://portal.azure.com/
:: - optional [azure_texttospeech]
set LINGU_AZURE_SPEECH_KEY=

:: Elevenlabs API Key  https://beta.elevenlabs.io/Elevenlabs
:: - optional [elevenlabs_texttospeech]
set LINGU_ELEVENLABS_SPEECH_KEY=

::  Google Cloud API key  https://console.cloud.google.com/
:: - optional [media_playout] (API key needs access to the YouTube Data API v3)
:: - optional [picture_search] (API key needs access to the Custom Search API)
set LINGU_GOOGLE_API_KEY=

::  Search engine ID / Suchmaschinen-ID  https://cse.google.com/cse/all
:: - optional [picture_search]
set LINGU_GOOGLE_CX_KEY=

::  Serp API key  https://serpapi.com/
:: - optional [google_information]
set LINGU_SERP_API_KEY=

::   OpenWeatherMap API Key  https://openweathermap.org/api
:: - optional [weather_forecast]
set LINGU_OPENWEATHERMAP_API_KEY=

:: Check if LINGU_OPENAI_API_KEY is set
if not defined LINGU_OPENAI_API_KEY (
    echo LINGU_OPENAI_API_KEY environment variable is not set. 
    echo OpenAI API Key expected in config.txt[openai_generator][api_key].
)

:: start linguflex
::────────────────────────────────────

TITLE LinguFlex
python linguflex.py
pause
cmd