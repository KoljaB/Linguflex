@echo off

call test_env\Scripts\activate.bat

set COQUI_MODEL_PATH=

:: OpenAI API Key  https://platform.openai.com/
:: - essential to run linguflex
set OPENAI_API_KEY=

:: Microsoft Azure API Key  https://portal.azure.com/
:: - optional [azure_texttospeech]
set AZURE_SPEECH_KEY=

set AZURE_SPEECH_REGION=

:: Elevenlabs API Key  https://beta.elevenlabs.io/Elevenlabs
:: - optional [elevenlabs_texttospeech]
set ELEVENLABS_API_KEY=

:: Google Cloud API key  https://console.cloud.google.com/
set GOOGLE_API_KEY=

:: Google Search engine ID / Suchmaschinen-ID  https://cse.google.com/cse/all
set GOOGLE_CX_KEY=
set GOOGLE_CSE_ID=

:: OpenWeatherMap API Key  https://openweathermap.org/api
set OPENWEATHERMAP_API_KEY=


python -m lingu.core.run

cmd 