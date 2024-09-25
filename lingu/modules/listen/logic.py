"""
Triggers:
- self.trigger("user_text", text)
- self.trigger("user_text_complete", text)
- self.trigger("user_audio_complete", user_bytes)
- self.trigger("recording_start")
- self.trigger("recording_stop")
- self.trigger("vad_start")
- self.trigger("wakeword_start")
- self.trigger("wakeword_end")
- self.trigger("recorded_chunk")
- self.trigger("volume_interrupt")
"""


from RealtimeSTT import AudioToTextRecorder
from lingu import cfg, log, Logic
import numpy as np
import threading
import time
import gc

main_recorder_model = cfg(
    "listen", "main_recorder_model", default="large-v2")
enable_realtime_transcription = bool(cfg(
    "listen", "enable_realtime_transcription", default=True))
realtime_recorder_model = cfg(
    "listen", "realtime_recorder_model", default="tiny")
realtime_processing_pause = float(cfg(
    "listen", "realtime_processing_pause", default=0.02))
webrtc_sensitivity = int(cfg(
    "listen", "webrtc_sensitivity", default=3))
min_length_of_recording = float(cfg(
    "listen", "min_length_of_recording", default=0.3))
min_gap_between_recordings = float(cfg(
    "listen", "min_gap_between_recordings", default=0.01))
wake_word_timeout = int(cfg(
    "listen", "wake_word_timeout", default=40))
silero_use_onnx = bool(cfg(
    "listen", "enable_realtime_transcription", default=False))
return_to_wakewords_after_silence = int(cfg(
    "listen", "return_to_wakewords_after_silence", default=20))
silero_sensitivity_normal = float(cfg(
    "listen", "silero_sensitivity_normal", default=0.2))
silero_sensitivity_music = float(cfg(
    "listen", "silero_sensitivity_music", default=0.01))
fast_silence_duration = float(cfg(
    "listen", "fast_post_speech_silence_duration", default=0.25))
long_term_noise_decay = float(cfg(
    "listen", "long_term_noise_decay", default=0.995))
short_term_noise_decay = float(cfg(
    "listen", "short_term_noise_decay", default=0.9))
allow_speech_interruption = bool(cfg(
    "listen", "allow_speech_interruption", default=True))
sentence_delimiters = cfg(
    "listen", "sentence_delimiters", default='.?!。')
wakeword_backend = cfg(
    "listen", "wakeword_backend", default="pvporcupine") # can be "pvporcupine" or "oww"
openwakeword_model_paths = cfg(
    "listen", "openwakeword_model_paths",
    default=None # for example: "suh_man_tuh.onnx,suh_mahn_thuh.onnx,ling_goo_flex.onnx"
    )
openwakeword_inference_framework = cfg(
    "listen", "openwakeword_inference_framework", default="onnx")
wake_word_buffer_duration = float(cfg(
    "listen", "wake_word_buffer_duration", default=1.0))
wake_words_sensitivity = float(cfg(
    "listen", "wake_words_sensitivity", default=0.35))



class ListenLogic(Logic):
    def __init__(self):
        super().__init__()

        self.set_ready = True
        self.recorder = None
        self.last_realtime_text = ""
        self.start_listen_event = threading.Event()
        self.speech_ready_event = threading.Event()
        self.listen_ready_event = threading.Event()
        self.recorder_active = True
        self.long_term_noise_level = 0.0
        self.current_noise_level = 0.0

        self.add_listener("playback_start", "music", self._on_playback_start)
        self.add_listener("playback_stop", "music", self._on_playback_stop)
        self.add_listener("speech_ready", "speech", self._on_speech_ready)
        self.add_listener(
            "audio_stream_stop",
            "speech",
            self._on_audio_stream_stop)
        self.add_listener(
            "symbol_mouse_enter",
            "*",
            self._on_wake_up)
        self.add_listener(
            "stop_recorder",
            "speech",
            self._on_stop_recorder)
        self.add_listener(
            "client_connected",
            "server",
            self._disable_recording)
        self.add_listener(
            "client_disconnected",
            "server",
            self._enable_recording)
        self.add_listener(
            "client_chunk_received",
            "server",
            self._client_chunk_received)

    def _client_chunk_received(self, data):
        self.recorder.feed_audio(data)

    def _disable_recording(self):
        self.state.set_text("🌐")
        log.inf("  [listen] client connected, disabling server microphone")
        self.recorder.set_microphone(False)

    def _enable_recording(self):
        self.state.set_text("")
        log.inf("  [listen] client disconnected, enabling server microphone")
        self.recorder.set_microphone(True)

    def sleep(self):
        self.start_listen_event.clear()
        self.recorder.abort()
        self.recorder.stop()
        self.state.set_active(False)
        self.state.set_disabled(True)

    def wakeup(self):
        self.recorder.recording_stop_time = 0
        self.state.set_disabled(False)
        self.recorder.wakeup()
        self.start_listen_event.set()
        self.recorder.listen_start = time.time()

    def set_lang_shortcut(self, lang_shortcut):
        log.inf(f"  [listen] setting language shortcut to {lang_shortcut}")
        self.state.language = lang_shortcut
        self.state.save()
        self.destroy_recorder()
        self.create_recorder()

    def _on_stop_recorder(self):
        log.inf("  [listen] stop recorder")
        self.sleep()

    def _on_audio_stream_stop(self):
        log.dbg("  [listen] audio stream stop")
        self.wakeup()

    def _on_speech_ready(self):
        self.speech_ready_event.set()

    def _on_wake_up(self):
        self.recorder.listen_start = time.time()

    def _realtime_transcription(self, text: str):
        text = text.strip()
        prob_sentence_end = False

        if text:
            prob_sentence_end = (
                len(self.last_realtime_text) > 0
                and text[-1] in sentence_delimiters
                and self.last_realtime_text[-1] in sentence_delimiters
            )

            if prob_sentence_end:
                self.recorder.post_speech_silence_duration = (
                    fast_silence_duration
                )

            self.last_realtime_text = text

        if not prob_sentence_end:
            self.recorder.post_speech_silence_duration = \
                self.state.end_of_speech_silence

        self.trigger("user_text", text)

    def _final_text(self, text):
        self.trigger("user_text_complete", text)

        user_bytes = self.recorder.last_transcription_bytes
        self.trigger("user_audio_complete", user_bytes)

        if hasattr(self, 'on_final_text'):
            self.on_final_text(text)

    def listen(self):
        self.start_listen_event.set()

    def init_finished(self):
        self.create_recorder()

    def create_recorder(self):
        self.recorder_active = True

        self.recording_worker_thread = threading.Thread(
            target=self._recording_worker
        )
        self.recording_worker_thread.daemon = True
        self.recording_worker_thread.start()

        self.listen()

    def destroy_recorder(self):
        if self.recording_worker_thread:
            self.recorder_active = False
            self.recorder.abort()
            self.recording_worker_thread.join()
            self.recording_worker_thread = None

    def _on_playback_start(self):
        self.recorder.silero_sensitivity = silero_sensitivity_music

        self.recorder.wake_word_activation_delay = 0

    def _on_playback_stop(self):
        self.recorder.silero_sensitivity = silero_sensitivity_normal
        self.recorder.wake_word_activation_delay = \
            return_to_wakewords_after_silence

    def toggle_mute(self):
        self.state.is_muted = not self.state.is_muted

        if self.state.is_muted:
            self.sleep()
        else:
            self.wakeup()

    def _recording_start(self):
        log.dbg("  [listen] recording start")
        self.recorder.post_speech_silence_duration = \
            self.state.end_of_speech_silence
        self.last_realtime_text = ""
        self.state.set_active(True)
        self.trigger("recording_start")

    def _recording_stop(self):
        log.dbg("  [listen] recording stop")
        self.state.set_active(False)
        self.start_listen_event.clear()
        self.state.set_disabled(True)
        self.trigger("recording_stop")

    def _vad_start(self):
        self.trigger("vad_start")

    def _wakeword_start(self):
        log.dbg(f"  [listen] listening to wakeword")
        self.trigger("wakeword_start")

    def _wakeword_end(self):
        log.dbg(f"  [listen] stopped listening to wakeword")
        self.trigger("wakeword_end")

    def _transcription_start(self):
        if hasattr(self, 'on_transcription_start'):
            self.on_transcription_start()

    def set_start_timeout(self, value):
        log.inf(f"  [listen] setting start timeout to {value:.1f} seconds")
        self.recorder.wake_word_activation_delay = value
        self.state.wake_word_activation_delay = value
        self.state.save()

    def set_end_timeout(self, value):
        log.inf(f"  [listen] setting end timeout to {value:.1f} seconds")
        self.recorder.post_speech_silence_duration = value
        self.state.end_of_speech_silence = value
        self.state.save()

    def get_levels(self, data, long_term_noise_level, current_noise_level):

        pegel = np.abs(np.frombuffer(data, dtype=np.int16)).mean()

        long_term_noise_level = \
            (long_term_noise_level * long_term_noise_decay
                + pegel * (1.0 - long_term_noise_decay))

        current_noise_level = \
            (current_noise_level * short_term_noise_decay
                + pegel * (1.0 - short_term_noise_decay))

        return pegel, long_term_noise_level, current_noise_level

    def _recorded_chunk(self, chunk):
        pegel, self.long_term_noise_level, self.current_noise_level = \
            self.get_levels(
                chunk,
                self.long_term_noise_level,
                self.current_noise_level)

        if self.state.interrupt_thresh > 0 and allow_speech_interruption:
            if pegel > self.state.interrupt_thresh:
                self.trigger("volume_interrupt")

        self.state.pegel = pegel
        self.trigger("recorded_chunk")

    def _recording_worker(self):
        lang = self.state.language
        if lang == "Auto":
            lang = ""

        # recorder construction parameters dictionary
        recorder_params = {
            'model': main_recorder_model,
            'language': lang,
            'wake_words': "Jarvis",
            'wake_words_sensitivity': wake_words_sensitivity,
            'spinner': False,
            'silero_sensitivity': silero_sensitivity_normal,
            'silero_use_onnx': silero_use_onnx,
            'webrtc_sensitivity': webrtc_sensitivity,
            'on_recording_start': self._recording_start,
            'on_recording_stop': self._recording_stop,
            'on_vad_detect_start': self._vad_start,
            'on_wakeword_detection_start': self._wakeword_start,
            'on_wakeword_detection_end': self._wakeword_end,
            'on_transcription_start': self._transcription_start,
            'post_speech_silence_duration': self.state.end_of_speech_silence,
            'min_length_of_recording': min_length_of_recording,
            'min_gap_between_recordings': min_gap_between_recordings,
            'wake_word_timeout': wake_word_timeout,
            'wake_word_activation_delay':
                self.state.wake_word_activation_delay,
            'wakeword_backend': wakeword_backend,
            'openwakeword_model_paths': openwakeword_model_paths,
            'openwakeword_inference_framework': openwakeword_inference_framework,
            'wake_word_buffer_duration': wake_word_buffer_duration,
            'enable_realtime_transcription': enable_realtime_transcription,
            'realtime_processing_pause': realtime_processing_pause,
            'realtime_model_type': realtime_recorder_model,
            'on_realtime_transcription_update': self._realtime_transcription,
            'on_recorded_chunk': self._recorded_chunk,
        }

        # log the parameters
        log.dbg("  [listen] creating recorder with parameters: "
                f"{recorder_params}")

        # Initialize the recorder with the unpacked parameters
        self.recorder = AudioToTextRecorder(**recorder_params)

        self.speech_ready_event.wait()
        self.start_listen_event.wait()

        self.ready()
        self.server_ready_event.wait()
        log.inf("  [listen] start listening")

        def final_text(text):
            if text:
                self._final_text(text)

        self.listen_ready_event.set()
        while (self.recorder_active):
            self.start_listen_event.wait()

            self.start_listen_event.clear()

            self.recorder.text(final_text)

        self.start_listen_event.clear()

        self.recorder.shutdown()
        del self.recorder
        self.recorder = None
        gc.collect()


if __name__ == '__main__':
    logic = ListenLogic()
