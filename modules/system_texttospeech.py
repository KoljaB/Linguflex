from core import TextToSpeechModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from distutils.command import clean
import pyttsx3
import re
import threading
from pygame import mixer
import time

voice = cfg('voice')

SYNTHESIS_FILE = 'system_speech_synthesis.wav' 

class TextToSpeech_System(TextToSpeechModule):
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        installed_voices = self.engine.getProperty('voices')
        log(DEBUG_LEVEL_MAX, f'  [pyttsx] available voices:')
        for installed_voice in installed_voices:
            log(DEBUG_LEVEL_MAX, f'    [pyttsx] {installed_voice}')
        if not voice is None:
            for installed_voice in installed_voices:
                if voice in installed_voice.name:
                    log(DEBUG_LEVEL_MAX, f'  [pyttsx] voice set to {installed_voice.name}')
                    self.engine.setProperty('voice', installed_voice.id)

    def init(self) -> None: 
        def microphone_recording_changed(is_recording):
            if is_recording: self.stop_audio()
        self.server.register_event("microphone_recording_changed", microphone_recording_changed)

    def remove_links(self, text):
        """
        Removes all links from a text, we don't want them to be spoken out
        """

        # matches most common URL formats
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

        # replace any matched patterns with an empty string
        no_links = re.sub(pattern, '', text)
        return no_links    

    def perform_text_to_speech(self, 
            request: Request) -> None: 
        
        spoken_text = self.remove_links(request.output)

        log(DEBUG_LEVEL_MAX, f'  [pyttsx] synthesizing speech for text [{spoken_text}]')

        self.engine.save_to_file(spoken_text, SYNTHESIS_FILE)
        self.engine.runAndWait()

        self.play_thread = threading.Thread(target=self.play_audio, args=(SYNTHESIS_FILE, request))
        self.play_thread.start()            

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
            log(DEBUG_LEVEL_MIN, f"  [pyttsx] ERROR synthesizing speech: {str(e)}")
            # call perform_text_to_speech on error with interruptable = False
            self.perform_text_to_speech(request, interruptable=False)

    def stop_audio(self):
        """Stops the audio being played"""
        if hasattr(self, 'audio_playing') and self.audio_playing and mixer.music.get_busy():  # check flag and if mixer is busy
            mixer.music.stop()
        if hasattr(self, 'play_thread') and self.play_thread.is_alive():
            self.play_thread.join()