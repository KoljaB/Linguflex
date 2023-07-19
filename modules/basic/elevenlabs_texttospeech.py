import json
import os
import re
import threading
import time
from core import TextToSpeechModule, Request, cfg, log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_MIN, DEBUG_LEVEL_ERR
from elevenlabs import voices, set_api_key, generate, save
from elevenlabs.api import Voice, VoiceSettings
from elevenlabs_texttospeech_helper import ConvertNumbersToText
from pygame import mixer


SYNTHESIS_FILE = 'elevenlabs_speech_synthesis.mp3'

class TextToSpeech_ElevenLabs(TextToSpeechModule):

    def __init__(self):
        self.language = cfg('language')
        self.log_voices = cfg('log_voices').lower() == 'true'
        self.api_key = cfg('api_key', env_key='ELEVENLABS_SPEECH_KEY')

        # Set API key for the ElevenLabs service
        set_api_key(self.api_key)

        # Print available voices into logging of desired
        if self.log_voices:
            voices_elevenlabs = voices()
            log(DEBUG_LEVEL_MAX, f"  [tts_eleven] Available voices: {voices_elevenlabs}")

        # Initialize text converter
        self.text_converter = ConvertNumbersToText()

        # Load available voices
        # current_directory = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(current_directory, f"elevenlabs_texttospeech.voices.{self.language}.json")
        file_path =  f"config/elevenlabs_texttospeech.voices.{self.language}.json"

        try:
            # Load voices from file
            with open(file_path, "r", encoding='utf-8') as file:
                self.available_voices = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Log error and use empty list as fallback
            log(DEBUG_LEVEL_ERR, f"  [tts_eleven] Error loading voices file: {e}")
            self.available_voices = []

    def init(self):
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
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        no_links = re.sub(pattern, '', text)
        return no_links

    def perform_text_to_speech(self, request: Request):

        output_optimized = self.text_converter.optimiere(request.output) if self.language == "de" else request.output

        # If 'character' attribute is present in the request, find the corresponding voice
        if hasattr(request, 'character'):
            log(DEBUG_LEVEL_MAX, f"  [tts_eleven] tts started, favoured voice {request.character}")
            selected_voice = None
            for voice in self.available_voices:
                if voice["voice"] == request.character:
                    selected_voice = voice
                    break
        else:
            log(DEBUG_LEVEL_MAX, f"  [tts_eleven] tts started, no favoured voice")

        # If 'character' attribute is not present or no matching voice was found, use the first available voice
        if not selected_voice and self.available_voices:
            selected_voice = self.available_voices[0]
            
        # If no voice available, use "Bella"
        if not selected_voice:
            selected_voice = "Bella"            

        spoken_text = self.remove_links(output_optimized)
        log(DEBUG_LEVEL_MAX, '  [tts_eleven] synthesizing speech for text [{}]'.format(spoken_text))

        if isinstance(selected_voice, dict):
            voice_object = Voice(
                voice_id=selected_voice["id"],
                name=selected_voice["name"],
                category=selected_voice["category"],
                settings=VoiceSettings(stability=float(selected_voice["stability"]), similarity_boost=float(selected_voice["similarity"]))
            )
            audio = generate(text=spoken_text, voice=voice_object, model="eleven_multilingual_v1")
        else:
            audio = generate(text=spoken_text, voice=selected_voice, model="eleven_multilingual_v1")

        save(audio, SYNTHESIS_FILE)
        # Play the audio in a new thread
        self.play_thread = threading.Thread(target=self.play_audio, args=(SYNTHESIS_FILE,))
        self.play_thread.start()

    def play_audio(self, file_path):
        """Plays the audio in the file specified by file_path"""
        mixer.music.load(file_path)
        mixer.music.play()
        self.audio_playing = True  # set flag
        while mixer.music.get_busy():
            time.sleep(0.1)
        self.audio_playing = False  # reset flag when finished

    def stop_audio(self):
        """Stops the audio being played"""
        if hasattr(self, 'audio_playing') and self.audio_playing and mixer.music.get_busy():  # check flag and if mixer is busy
            mixer.music.stop()
        if hasattr(self, 'play_thread') and self.play_thread.is_alive():
            self.play_thread.join()


#  voice_id='21m00Tcm4TlvDq8ikWAM', name='Rachel', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='AZnzlk1XvdvUeBnXmlld', name='Domi', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='EXAVITQu4vr4xnSDxMaL', name='Bella', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='ErXwobaYiN019PkySvjV', name='Antoni', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='MF3mGyEYCl7XYWbV9V6O', name='Elli', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='TxGEqnHWrfWFTfGW9XjX', name='Josh', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='VR6AewLTigWG4xSOukaG', name='Arnold', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='pNInz6obpgDQGcFmaJgB', name='Adam', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='yoZ06aMxZJJ28mfd3POQ', name='Sam', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75