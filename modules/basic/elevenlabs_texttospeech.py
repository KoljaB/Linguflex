import json
import os
from core import TextToSpeechModule, Request, cfg, log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_MIN, DEBUG_LEVEL_ERR
from elevenlabs import voices, set_api_key, generate, play
from elevenlabs.api import Voice, VoiceSettings
from elevenlabs_texttospeech_helper import ConvertNumbersToText

class TextToSpeech_ElevenLabs(TextToSpeechModule):
    """
    Text to speech implementation for ElevenLabs service.
    """

    def __init__(self):
        """
        Initialize the text to speech module with settings from the configuration and loading available voices.
        """

        # Get configuration settings
        self.voice = cfg('voice')
        self.language = cfg('language')
        self.log_voices = cfg('log_voices').lower() == 'true'
        self.api_key = cfg('api_key', 'ELEVENLABS_SPEECH_KEY')

        # Set API key for the ElevenLabs service
        set_api_key(self.api_key)

        # Initialize text converter
        self.text_converter = ConvertNumbersToText()

        # Load available voices
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, f"elevenlabs_texttospeech.voices.{self.language}.json")
        
        try:
            # Load voices from file
            with open(file_path, "r", encoding='utf-8') as file:
                self.available_voices = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Log error and use empty list as fallback
            log(DEBUG_LEVEL_ERR, f"Error loading voices file: {e}")
            self.available_voices = []

        # Log voices if configured to do so
        if self.log_voices:
            installed_voices = voices()
            log(DEBUG_LEVEL_MIN, f"  [tts_eleven] installed voices: {installed_voices}")
        log(DEBUG_LEVEL_MAX, f"  [tts_eleven] available voices: {self.available_voices}")

    def is_voice_available(self, request: Request) -> bool:
        """
        Check if the requested voice is available.

        Returns:
            A boolean indicating if the voice is available.
        """

        # Check if any voice in available voices matches the requested one
        return any(voice["voice"] == request.character for voice in self.available_voices)

    def perform_text_to_speech(self, request: Request) -> None:
        """
        Perform text to speech using the ElevenLabs service.
        """

        # Optimize output if language is German
        output_optimized = self.text_converter.optimiere(request.output_user) if self.language == "de" else request.output_user

        # Log start of TTS process and output
        log(DEBUG_LEVEL_MAX, f"  [tts_eleven] tts started, favoured voice {request.character}")
        log(DEBUG_LEVEL_MAX, '  [tts_eleven] output [{}]'.format(output_optimized))

        # Select requested voice if available, fallback to first available or "Bella" if none
        selected_voice = next((voice for voice in self.available_voices if voice["voice"] == request.character), self.available_voices[0] if self.available_voices else "Bella")

        # If selected voice is a dict, create Voice object
        if isinstance(selected_voice, dict):
            voice_object = Voice(
                voice_id=selected_voice["id"],
                name=selected_voice["name"],
                category=selected_voice["category"],
                settings=VoiceSettings(stability=float(selected_voice["stability"]), similarity_boost=float(selected_voice["similarity"]))
            )
            # Generate audio using the selected voice
            audio = generate(text=output_optimized, voice=voice_object, model="eleven_multilingual_v1")        
        else:
            # Generate audio using the fallback voice
            audio = generate(text=output_optimized, voice=selected_voice, model="eleven_multilingual_v1")
        
        # Play the generated audio
        play(audio)

#  voice_id='21m00Tcm4TlvDq8ikWAM', name='Rachel', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='AZnzlk1XvdvUeBnXmlld', name='Domi', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='EXAVITQu4vr4xnSDxMaL', name='Bella', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='ErXwobaYiN019PkySvjV', name='Antoni', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='MF3mGyEYCl7XYWbV9V6O', name='Elli', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='TxGEqnHWrfWFTfGW9XjX', name='Josh', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='VR6AewLTigWG4xSOukaG', name='Arnold', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='pNInz6obpgDQGcFmaJgB', name='Adam', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75
#  voice_id='yoZ06aMxZJJ28mfd3POQ', name='Sam', category='premade', settings=VoiceSettings(stability=0.75, similarity_boost=0.75