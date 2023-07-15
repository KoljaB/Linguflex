from core import InputModule, Request, cfg, log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, play_sound
import wave
import numpy as np
import pyaudio
import tempfile
import os
import time
import struct
import pvporcupine # needs v1.9.5 (!)

mic_debug_show_volume = cfg('debug_show_volume').lower() == 'true'
volume_start_recording = int(cfg('volume_start_recording'))
volume_stop_recording = int(cfg('volume_stop_recording'))
tts = cfg('tts', default='default')
wake_words = cfg('wake_words', default='jarvis')
wake_words_list = [word.strip() for word in wake_words.split(',')]
wake_words_sensitivity = cfg('wake_words_sensitivity', default=0.4)
sensitivity_list = [float(wake_words_sensitivity) for _ in range(len(wake_words_list))]
ema_ambient_noise_level = float(cfg('ema_ambient_noise_level', default=0.995))
ema_current_noise_level = float(cfg('ema_current_noise_level', default=0.9))
end_of_sentence_silence_length = float(cfg('end_of_sentence_silence_length', default=1.2))

MIC_AUDIO_FORMAT = pyaudio.paInt16
MIC_AUDIO_CHANNEL_COUNT = 1
MIC_FILENAME_RECORDINGS = 'linguflex_microphone_recording.wav'
MIC_ORIGIN = 'microphone'

class MicListenerModule(InputModule):
    def __init__(self):
        log(DEBUG_LEVEL_MAX, '  [microphone] open audio stream')
        self.wave_path = None
        self.is_recording = False
        self.wavefile_available = False
        self.last_log_time = None 
        self.recording_allowed = True
        self.wakeword_detection_active = True

        log(DEBUG_LEVEL_MAX, f'  [microphone] wake words {wake_words_list}, sensitivities {sensitivity_list}')
        self.porcupine = pvporcupine.create(keywords=wake_words_list, sensitivities=sensitivity_list)
        self.vad_counter = 0.0
        self.vad_reset_counter = 0.0
        self.ema_max_volume = 0.0
        self.current_noise_level = 0.0
        self.ambient_noise_level = 0.0
        self.current_noise_before_talk = 0.0

        try:
            self.audio, self.stream, self.frames = self.start_recording()
        except OSError as e:
            log(DEBUG_LEVEL_OFF, f'  [microphone] error in opening audio stream: {str(e)}')
            self.audio = None
            self.stream = None
            self.frames = []
    
    def init(self) -> None: 
        def set_recording(recording_allowed):
            self.recording_allowed = recording_allowed
            log(DEBUG_LEVEL_MID, f'  [microphone] recording allowed: {recording_allowed}')
            self.server.set_event("microphone_recording_allowed_changed", recording_allowed)

            if not recording_allowed and self.wakeword_detection_active:
                self.wakeword_detection_active = False
                self.server.set_event("wakeword_detection_active_changed", False)

        self.server.register_event("microphone_recording_allowed", set_recording)

        def set_wakeword_detection(wakeword_detection_active):
            self.wakeword_detection_active = wakeword_detection_active
            log(DEBUG_LEVEL_MID, f'  [microphone] wakeword detection active: {wakeword_detection_active}')
            self.server.set_event("wakeword_detection_active_changed", wakeword_detection_active)

            if wakeword_detection_active and not self.recording_allowed:
                self.recording_allowed = True
                self.server.set_event("microphone_recording_allowed_changed", True)

        self.server.register_event("wakeword_detection_active", set_wakeword_detection)

    def start_recording(self):
        try:
            audio = pyaudio.PyAudio()
            
            stream = audio.open(
                rate=self.porcupine.sample_rate,
                format=MIC_AUDIO_FORMAT,
                channels=MIC_AUDIO_CHANNEL_COUNT, 
                input=True, 
                frames_per_buffer=self.porcupine.frame_length)
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
                pass  
            
        if self.stream is not None:
            data = self.stream.read(self.porcupine.frame_length)

            wakeword_detected = False
            if self.wakeword_detection_active:
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, data)
                wakeword_index = self.porcupine.process(pcm)
                wakeword_detected = wakeword_index >= 0
                if wakeword_detected:
                    log(DEBUG_LEVEL_MIN, f'  [microphone] wake word "{wake_words_list[wakeword_index]}" detected')

            np_data = np.frombuffer(data, dtype=np.int16)
            pegel = np.abs(np_data).mean()
            if mic_debug_show_volume: 
                log(DEBUG_LEVEL_MIN, f'  [microphone] volume: {pegel}')

            if self.wakeword_detection_active:
                start_recording = wakeword_detected and self.recording_allowed and not self.is_recording
            else:
                start_recording = self.recording_allowed and not self.is_recording and pegel > volume_start_recording

            self.ambient_noise_level = self.ambient_noise_level * ema_ambient_noise_level + pegel * (1.0 - ema_ambient_noise_level)
            self.current_noise_level = self.current_noise_level * ema_current_noise_level + pegel * (1.0 - ema_current_noise_level)

            if start_recording:
                play_sound("recording_start")
                self.ema_max_volume = 0.0
                self.recording_start_time = time.time()
                log(DEBUG_LEVEL_MID, '  [microphone] recording')
                self.is_recording = True
                self.server.set_event("microphone_recording_changed", self.is_recording)
                self.current_noise_before_talk = self.ambient_noise_level

            if self.is_recording:
                self.frames.append(data)
                if self.current_noise_level > self.ema_max_volume:
                    self.ema_max_volume = self.current_noise_level

                # end of sentence detection  (when recording was started with wake word)
                if self.ema_max_volume > self.ambient_noise_level * 1.3 and self.current_noise_level < self.current_noise_before_talk * 1.1 and time.time() - self.recording_start_time > 2:
                    if self.wakeword_detection_active and time.time() - self.last_voice_detection_time > end_of_sentence_silence_length:
                        log(DEBUG_LEVEL_MID, f'  [microphone] stopped recording (volume returned to mean for {end_of_sentence_silence_length}s)')
                        self.stop_recording(self.audio, self.stream, self.frames)
                        self.audio, self.stream, self.frames = self.start_recording()
                else:
                    self.last_voice_detection_time = time.time()

                if pegel < volume_stop_recording or not self.recording_allowed:
                    log(DEBUG_LEVEL_MID, '  [microphone] stopped recording (muted or deactivated)')
                    self.stop_recording(self.audio, self.stream, self.frames)
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
        with wave.open(self.wave_path, 'wb') as wave_file:
            wave_file.setnchannels(MIC_AUDIO_CHANNEL_COUNT)
            wave_file.setsampwidth(audio.get_sample_size(MIC_AUDIO_FORMAT))
            wave_file.setframerate(self.porcupine.sample_rate)            
            wave_file.writeframes(b''.join(frames))
        self.wavefile_available = True
        play_sound("recording_stop")
        self.is_recording = False
        self.server.set_event("microphone_recording_changed", self.is_recording)

    def create_audio_input(self,
            request: Request):
        if self.wavefile_available:
            self.wavefile_available = False
            request.audio = self.wave_path
            request.tts = tts
            request.user_id = 'Microphone'