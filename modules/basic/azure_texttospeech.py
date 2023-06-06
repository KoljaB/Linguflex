import sys
sys.path.insert(0, '..')
import azure.cognitiveservices.speech as speechsdk
import pyaudio
import wave
import os

from linguflex_interfaces import TextToSpeechModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage

set_section('azure_texttospeech')

API_KEY_NOT_FOUND_ERROR_MESSAGE = 'Azure Speech API-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_AZURE_SPEECH_KEY.'

# Import Azure Speech API-Key from either registry (LINGU_AZURE_SPEECH_KEY) or config file tts_azure/azure_speech_api_key
api_key = os.environ.get('LINGU_AZURE_SPEECH_KEY')
if api_key is None:
    try:
        api_key = cfg[get_section()]['azure_speech_api_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if api_key is None:
    raise ValueError(API_KEY_NOT_FOUND_ERROR_MESSAGE)

# Read module configuration
try:
    region = cfg[get_section()].get('azure_speech_region', 'germanywestcentral')
    voice = cfg[get_section()].get('voice', 'de-DE-AmalaNeural')
    language = cfg[get_section()].get('language', 'de-DE')
    rate_percent = cfg[get_section()].getint('rate_percent', '30')
    pitch_percent = cfg[get_section()].getint('pitch_percent', '2')
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))

class TextToSpeechModule_Azure(TextToSpeechModule_IF):
    def __init__(self) -> None:
        speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
        speech_config.speech_synthesis_language = language
        speech_config.speech_synthesis_voice_name = voice
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    def perform_text_to_speech(self, 
            message: LinguFlexMessage) -> None: 
        ssml_string = f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{language}'><voice name='{voice}'><prosody rate='{rate_percent}%' pitch='{pitch_percent}%'>{message.output_user}</prosody></voice></speak>"
        speech_synthesis_result = self.speech_synthesizer.speak_ssml_async(ssml_string).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            log(DEBUG_LEVEL_MAX, '  [tts_azure] speech synthesized for text [{}]'.format(message.output_user))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            log(DEBUG_LEVEL_MID, '  [tts_azure] speech synthesis canceled: {}'.format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    log(DEBUG_LEVEL_MID, '[tts_azure] error details: {}'.format(cancellation_details.error_details))
                    log(DEBUG_LEVEL_MID, '[tts_azure] did you set the speech resource key and region values?')

# Available Voices in German:
#
# de-DE-BerndNeural (Male)
# de-DE-ChristophNeural (Male)
# de-DE-ConradNeural1 (Male)
# de-DE-KasperNeural (Male)
# de-DE-KillianNeural (Male)
# de-DE-KlausNeural (Male)
# de-DE-RalfNeural (Male)
#
# de-DE-AmalaNeural (Female)
# de-DE-ElkeNeural (Female)
# de-DE-GiselaNeural (Female, Child)
# # de-DE-KatjaNeural (Female)
# de-DE-KlarissaNeural (Female)
# de-DE-LouisaNeural (Female)
# de-DE-MajaNeural (Female)
# de-DE-TanjaNeural (Female)