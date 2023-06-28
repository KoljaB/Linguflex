from core import InputModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
import wave
import numpy as np
import pyaudio
import tempfile
import os
import time

mic_debug_show_volume = cfg('debug_show_volume').lower() == 'true'
volume_start_recording = int(cfg('volume_start_recording'))
volume_stop_recording = int(cfg('volume_stop_recording'))
audio_sampling_rate = int(cfg('sampling_rate'))
tts = cfg('tts', default='default')

MIC_AUDIO_FORMAT = pyaudio.paInt16
MIC_AUDIO_CHANNEL_COUNT = 1
MIC_AUDIO_CHUNK_SIZE = 1024
MIC_FILENAME_RECORDINGS = 'linguflex_microphone_recording.wav'
MIC_ORIGIN = 'microphone'

class MicListenerModule(InputModule):
    def __init__(self):
        log(DEBUG_LEVEL_MAX, '  [microphone] open audio stream')
        self.wave_path = None
        self.is_recording = False
        self.wavefile_available = False
        self.last_log_time = None 
        try:
            self.audio, self.stream, self.frames = self.start_recording()
        except OSError as e:
            log(DEBUG_LEVEL_OFF, f'  [microphone] error in opening audio stream: {str(e)}')
            
            self.audio = None
            self.stream = None
            self.frames = []

    def start_recording(self):
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=MIC_AUDIO_FORMAT, channels=MIC_AUDIO_CHANNEL_COUNT, rate=audio_sampling_rate, input=True, frames_per_buffer=MIC_AUDIO_CHUNK_SIZE)
        except OSError as e:
            log(DEBUG_LEVEL_OFF, f'  [microphone] error in opening audio stream: {str(e)}')
            return None, None, []
        frames = []
        log(DEBUG_LEVEL_MID, '  [microphone] listening')
        return audio, stream, frames     
    
    def cycle(self,
            request: Request):

        if self.stream is None:
            current_time = time.time()
            if self.last_log_time is None or current_time - self.last_log_time >= 5:
                log(DEBUG_LEVEL_OFF, '  [microphone] stream is not available')
                self.last_log_time = current_time
            try:
                self.audio, self.stream, self.frames = self.start_recording()
            except OSError:
                pass  # Still no default output device available, ignore and continue        
            
        if self.stream is not None:
            data = self.stream.read(MIC_AUDIO_CHUNK_SIZE)
            np_data = np.frombuffer(data, dtype=np.int16)
            pegel = np.abs(np_data).mean()
            if mic_debug_show_volume: 
                log(DEBUG_LEVEL_MIN, f'  [microphone] volume: {pegel}')
            if not self.is_recording and pegel > volume_start_recording:
                log(DEBUG_LEVEL_MID, '  [microphone] recording')
                self.is_recording = True
            if self.is_recording:
                self.frames.append(data)
                if pegel < volume_stop_recording:
                    log(DEBUG_LEVEL_MID, '  [microphone] stopped recording')
                    if self.audio is not None and self.stream is not None and self.frames is not None: 
                        self.stop_recording(self.audio, self.stream, self.frames) 
                        # Audio now available at path MIC_FILENAME_RECORDINGS                                
                        self.is_recording = False
                        self.audio, self.stream, self.frames = self.start_recording()    
        else:
            current_time = time.time()
            if self.last_log_time is None or current_time - self.last_log_time >= 5:
                log(DEBUG_LEVEL_OFF, '  [microphone] stream is not available')
                self.last_log_time = current_time

    def stop_recording(self, 
            audio,
            stream,
            frames):
        stream.stop_stream()
        stream.close()
        audio.terminate()
        temp_file_path = tempfile.gettempdir()
        self.wave_path = os.path.join(temp_file_path, MIC_FILENAME_RECORDINGS)
        # Write the audio into a wave file
        with wave.open(self.wave_path, 'wb') as wave_file:
            wave_file.setnchannels(MIC_AUDIO_CHANNEL_COUNT)
            wave_file.setsampwidth(audio.get_sample_size(MIC_AUDIO_FORMAT))
            wave_file.setframerate(audio_sampling_rate)
            wave_file.writeframes(b''.join(frames))
        self.wavefile_available = True

    def create_audio_input(self,
            request: Request):
        if self.wavefile_available:
            self.wavefile_available = False
            request.audio = self.wave_path
            request.tts = tts
            request.user_id = 'Microphone'