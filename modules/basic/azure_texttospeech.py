import azure.cognitiveservices.speech as speechsdk
import json
import os
import re
import threading
from pygame import mixer
import time
from core import TextToSpeechModule, Request, cfg, log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_MID, DEBUG_LEVEL_MIN, DEBUG_LEVEL_ERR

SYNTHESIS_FILE = 'azure_speech_synthesis.wav' 

class TextToSpeech_Azure(TextToSpeechModule):
    """
    Text to speech implementation for Azure Cognitive Services.
    """

    def __init__(self):
        """
        Initialize the text to speech module with settings from the configuration and load available voices.
        """
        
        # Get configuration settings
        self.region = cfg('region')
        self.language = cfg('language')
        self.language_tag = cfg('language_tag')
        self.log_output = cfg('log_output').lower() == 'true'
        self.api_key = cfg('api_key', env_key='AZURE_SPEECH_KEY')

        # Load available voices
        # current_directory = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(current_directory, f"azure_texttospeech.voices.{self.language}.json")
        file_path =  f"config/azure_texttospeech.voices.{self.language}.json"

        try:
            with open(file_path, "r", encoding='utf-8') as file:
                self.available_voices = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            log(DEBUG_LEVEL_ERR, f"Error loading voices file: {e}")
            self.available_voices = []

        log(DEBUG_LEVEL_MAX, f"  [tts_azure] available voices: {self.available_voices}")

    def init(self) -> None: 
        def microphone_recording_changed(is_recording):
            if is_recording: self.stop_audio()
        self.server.register_event("microphone_recording_changed", microphone_recording_changed)

    def is_voice_available(self, 
            request: Request) -> bool:
        """
        Check if the requested voice is available.

        Returns:
            A boolean indicating if the voice is available.
        """
        if not hasattr(request, 'character'):
            return False        
        
        return any(voice["voice"] == request.character for voice in self.available_voices)
    
    def remove_links(self, text):
        """
        Removes all links from a text, we don't want them to be spoken out
        """

        # matches most common URL formats
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        # replace any matched patterns with an empty string
        no_links = re.sub(pattern, '', text)
        return no_links    

    def perform_text_to_speech(self, request: Request, interruptable = True) -> None: 
        """
        Perform text to speech using Azure Cognitive Services.
        """

        # Default voice
        selected_voice = {
            "voice": "Killian",
            "name": "de-DE-KillianNeural",
            "rate": "15",
            "pitch": "0"
        }

        if hasattr(request, 'character'):
            log(DEBUG_LEVEL_MAX, f"  [tts_azure] tts started, favoured voice {request.character}")
            # Find the requested voice
            for voice in self.available_voices:
                if voice["voice"] == request.character:
                    selected_voice = voice
                    log(DEBUG_LEVEL_MAX, f"  [tts_azure] favoured voice {request.character} found: {selected_voice['name']}")
        else:
            log(DEBUG_LEVEL_MAX, f"  [tts_azure] tts started, no favoured voice")


        spoken_text = self.remove_links(request.output)

        # Create SSML string for speech synthesis
        ssml_string = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{self.language_tag}">
            <voice name="{selected_voice["name"]}">
                <prosody rate="{selected_voice["rate"]}%" pitch="{selected_voice["pitch"]}%">
                    {spoken_text}
                </prosody>
            </voice>
        </speak>        
        """

        if self.log_output:
            log(DEBUG_LEVEL_MAX, f'  [tts_azure] synthesizing speech for ssml [{spoken_text}]')

        speech_config = speechsdk.SpeechConfig(subscription=self.api_key, region=self.region)
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
        speech_config.speech_synthesis_language = self.language_tag
        speech_config.speech_synthesis_voice_name = selected_voice["name"]

        if interruptable:
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

            # Initiate speech synthesis.
            self.result_future = self.speech_synthesizer.speak_ssml_async(ssml_string).get()
            speech_synthesis_result = self.result_future
            self.stream = speechsdk.AudioDataStream(speech_synthesis_result)
            self.stream.save_to_wav_file(SYNTHESIS_FILE)

            # Create a new thread to play the audio and start it
            self.play_thread = threading.Thread(target=self.play_audio, args=(SYNTHESIS_FILE, request))
            self.play_thread.start()            
        else:
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            def synthesis_thread():
                # Perform speech synthesis
                speech_synthesis_result = self.speech_synthesizer.speak_ssml_async(ssml_string).get()

                # Log the result
                if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    log(DEBUG_LEVEL_MAX, '  [tts_azure] speech synthesized for text [{}]'.format(request.output))
                elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_synthesis_result.cancellation_details
                    log(DEBUG_LEVEL_MID, '  [tts_azure] speech synthesis canceled: {}'.format(cancellation_details.reason))
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        if cancellation_details.error_details:
                            log(DEBUG_LEVEL_MID, '[tts_azure] error details: {}'.format(cancellation_details.error_details))
                            log(DEBUG_LEVEL_MID, '[tts_azure] did you set the speech resource key and region values?')

            # Start a new thread for the speech synthesis
            synthesis_thread = threading.Thread(target=synthesis_thread)
            synthesis_thread.start()            

    def play_audio(self, file_path, request):
        """Plays the audio in the file specified by file_path"""
        try:
            mixer.music.load(file_path)
            mixer.music.play()
            self.audio_playing = True  # set flag
            while mixer.music.get_busy():
                time.sleep(0.1)
            self.audio_playing = False  # reset flag when finished
        except Exception as e:
            log(DEBUG_LEVEL_MIN, f"  [tts_azure] ERROR synthesizing speech: {str(e)}")
            # call perform_text_to_speech on error with interruptable = False
            self.perform_text_to_speech(request, interruptable=False)

    def stop_audio(self):
        """Stops the audio being played"""
        if hasattr(self, 'audio_playing') and self.audio_playing and mixer.music.get_busy():  # check flag and if mixer is busy
            mixer.music.stop()
        if hasattr(self, 'play_thread') and self.play_thread.is_alive():
            self.play_thread.join()