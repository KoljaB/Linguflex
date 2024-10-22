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


from RealtimeSTT import AudioToTextRecorderClient
from lingu import cfg, log, Logic, prompt, is_testmode
import numpy as np
import threading
import base64
import queue
import time
import gc
from difflib import SequenceMatcher
from dataclasses import dataclass
from typing import Deque
from collections import deque

IS_DEBUG = False


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
silero_deactivity_detection = bool(cfg(
    "listen", "silero_deactivity_detection", default=False))
beam_size = int(cfg(
    "listen", "beam_size", default=5))
beam_size_realtime = int(cfg(
    "listen", "beam_size", default=3))
delay_wakeup_after_assistant_speech = float(cfg(
    "listen", "delay_wakeup_after_assistant_speech", default=0.1)) # compensate for room hall etc
rapid_sentence_end_duration = float(cfg(
    "listen", "rapid_sentence_end_duration", default=0.1))
fast_sentence_end_silence_duration = float(cfg(
    "listen", "fast_sentence_end_silence_duration", default=0.1))
input_device_index = int(cfg(
    "listen", "input_device_index", default=-1))
early_transcription_on_silence = int(cfg(
    "listen", "early_transcription_on_silence", default=0))
use_main_model_for_realtime = bool(cfg(
    "listen", "use_main_model_for_realtime", default=False))


end_of_sentence_detection_pause = float(cfg(
    "listen", "end_of_sentence_detection_pause", default=1.2))
mid_sentence_detection_pause = float(cfg(
    "listen", "mid_sentence_detection_pause", default=2.4))
unknown_sentence_detection_pause = float(cfg(
    "listen", "unknown_sentence_detection_pause", default=1.8))
use_llm_sentence_end_detection = bool(cfg(
    "listen", "end_of_sentence_detection_pause", default=False))
rapid_sentence_end_detection = float(cfg(
    "listen", "rapid_sentence_end_detection", default=0.4))
hard_break_even_on_background_noise = float(cfg(
    "listen", "hard_break_even_on_background_noise", default=3.0))
hard_break_even_on_background_noise_min_texts = int(cfg(
    "listen", "hard_break_even_on_background_noise_min_texts", default=3))
hard_break_even_on_background_noise_min_similarity = float(cfg(
    "listen", "hard_break_even_on_background_noise_min_similarity", default=0.99))
hard_break_even_on_background_noise_min_chars = int(cfg(
    "listen", "hard_break_even_on_background_noise_min_chars", default=15))

compute_type = cfg(
    "listen", "compute_type",
    default = "default"
    )


@dataclass
class TextEntry:
    text: str
    timestamp: float


class ListenLogic(Logic):
    def __init__(self):
        super().__init__()

        self.set_ready = True
        self.recorder = None
        self.last_realtime_text = ""
        self.start_listen_event = threading.Event()
        self.speech_ready_event = threading.Event()
        self.listen_ready_event = threading.Event()
        self.text_queue = queue.Queue()
        self.recorder_active = True
        self.long_term_noise_level = 0.0
        self.current_noise_level = 0.0
        self.prob_sentence_end_start_time = None
        self.text_history: Deque[TextEntry] = Deque()
        self.max_history_age = 1.0  # 1 second
        self.speech_finished_cache = {}
        self.prev_text = ""
        self.text_time_deque = deque()
        # self.abrupt_stop = False

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

        self.worker_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.worker_thread.start()

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
        self.recorder.clear_audio_queue()
        self.recorder.set_parameter("recording_stop_time", 0)
        # self.recorder.recording_stop_time = 0
        self.state.set_disabled(False)
        self.recorder.wakeup()
        self.start_listen_event.set()
        self.recorder.set_parameter("listen_start",time.time())
        #self.recorder.listen_start = 

    def set_lang_shortcut(self, lang_shortcut):
        log.inf(f"  [listen] setting language shortcut to {lang_shortcut}")
        self.state.language = lang_shortcut
        self.state.save()
        self.destroy_recorder()
        self.create_recorder()

    def _on_stop_recorder(self):
        log.inf("  [listen] stop recorder")
        self.sleep()

    def delayed_wakeup(self):
        log.dbg(f"Delaying wakeup for {delay_wakeup_after_assistant_speech} seconds")
        time.sleep(delay_wakeup_after_assistant_speech)
        self.wakeup()

    def _on_audio_stream_stop(self):
        log.dbg("  [listen] audio stream stop")
        threading.Thread(
            target=self.delayed_wakeup
        ).start()

    def _on_speech_ready(self):
        self.speech_ready_event.set()

    def _on_wake_up(self):
        self.recorder.set_parameter("listen_start",time.time())        
        #self.recorder.listen_start = time.time()

    def _realtime_transcription(self, text: str):
        text = text.strip()
        current_time = time.time()

        # Remove old entries
        self.text_history = Deque([entry for entry in self.text_history if current_time - entry.timestamp <= self.max_history_age])

        # Add new entry
        self.text_history.append(TextEntry(text, current_time))

        self.trigger("user_text", text)
        self.text_queue.put(text)


    def _final_text(self, text):
        post_speech_silence_duration = self.recorder.get_parameter("post_speech_silence_duration")
        log.inf(f"  [listen] speech end detected, post_speech_silence_duration: {post_speech_silence_duration}")
        prompt.reset()

        self.trigger("before_user_text_complete", text)
        self.trigger("user_text_complete", text)

        # last_transcription_bytes = self.recorder.get_parameter("last_transcription_bytes_b64")
        # decoded_bytes = base64.b64decode(last_transcription_bytes)

        # # Step 2: Reconstruct the np.int16 array from the decoded bytes
        # audio_array = np.frombuffer(decoded_bytes, dtype=np.int16)

        # # Step 3: (Optional) If the original data was normalized, convert to np.float32 and normalize
        # INT16_MAX_ABS_VALUE = 32768.0
        # normalized_audio = audio_array.astype(np.float32) / INT16_MAX_ABS_VALUE        
        # self.trigger("user_audio_complete", normalized_audio)

        if hasattr(self, 'on_final_text'):
            self.on_final_text(text)

        if IS_DEBUG: print(f"SENTENCE: post_speech_silence_duration: {post_speech_silence_duration}")
        # self.recorder.post_speech_silence_duration = unknown_sentence_detection_pause
        print(f"_final_text setting post_speech_silence_duration to {unknown_sentence_detection_pause}")
        self.recorder.set_parameter("post_speech_silence_duration", unknown_sentence_detection_pause)
        text = self.preprocess_text(text)
        text = text.rstrip()
        self.text_time_deque.clear()
        if text.endswith("..."):
            text = text[:-2]
                
        self.prev_text = ""

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
        self.recorder.set_parameter("silero_sensitivity",silero_sensitivity_music)
        # self.recorder.silero_sensitivity = silero_sensitivity_music

        self.recorder.set_parameter("wake_word_activation_delay", 0)
        #self.recorder.wake_word_activation_delay = 0

    def _on_playback_stop(self):
        self.recorder.set_parameter("silero_sensitivity",silero_sensitivity_normal)
        # self.recorder.silero_sensitivity = silero_sensitivity_normal

        self.recorder.set_parameter("wake_word_activation_delay", return_to_wakewords_after_silence)
        # self.recorder.wake_word_activation_delay = \
        #     return_to_wakewords_after_silence

    def toggle_mute(self):
        self.state.is_muted = not self.state.is_muted

        if self.state.is_muted:
            self.sleep()
        else:
            self.wakeup()

    def _recording_start(self):
        log.dbg("  [listen] recording start")
        print(f"_recording_start setting post_speech_silence_duration to {self.state.end_of_speech_silence} (self.state.end_of_speech_silence)")
        self.recorder.set_parameter("post_speech_silence_duration", self.state.end_of_speech_silence)

        # self.recorder.post_speech_silence_duration = \
        #     self.state.end_of_speech_silence
        self.last_realtime_text = ""
        self.state.set_active(True)
        self.trigger("recording_start")

    def _recording_stop(self):
        log.dbg("  [listen] recording stop")
        self.state.set_active(False)
        self.start_listen_event.clear()
        self.state.set_disabled(True)
        self.trigger("recording_stop")
        log.dbg("  [listen] recording stop triggered")

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
        self.recorder.set_parameter("wake_word_activation_delay", value)
        
        # self.recorder.wake_word_activation_delay = value
        self.state.wake_word_activation_delay = value
        self.state.save()

    def set_end_timeout(self, value):
        log.inf(f"  [listen] setting end timeout to {value:.1f} seconds")
        print(f"set_end_timeout setting post_speech_silence_duration to {value} (value)")
        self.recorder.set_parameter("post_speech_silence_duration", value)
        # self.recorder.post_speech_silence_duration = value
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

        input_device_index = int(cfg("listen", "input_device_index", default=-1))
        # print(f"input_device_index: {input_device_index}")
    

        if input_device_index == -1:
            input_device_index = None

        # recorder construction parameters dictionary
        recorder_params = {
            'model': main_recorder_model,
            'compute_type' : compute_type,
            'input_device_index': input_device_index,
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
            'use_main_model_for_realtime' : use_main_model_for_realtime,
            'on_realtime_transcription_update': self._realtime_transcription,
            'on_recorded_chunk': self._recorded_chunk,
            'silero_deactivity_detection': silero_deactivity_detection,
            'beam_size': beam_size,
            'beam_size_realtime': beam_size_realtime,
            'initial_prompt': (
                "End incomplete sentences with ellipses.\n"
                "Examples:\n"
                "Complete: The sky is blue.\n"
                "Incomplete: When the sky...\n"
                "Complete: She walked home.\n"
                "Incomplete: Because he...\n"
            )
        }

        # log the parameters
        log.dbg("  [listen] creating recorder with parameters: "
                f"{recorder_params}")

        # Initialize the recorder with the unpacked parameters
        self.recorder = AudioToTextRecorderClient(**recorder_params)

        self.speech_ready_event.wait()
        self.start_listen_event.wait()

        self.ready()
        self.server_ready_event.wait()
        if not is_testmode():
            log.inf("  [listen] start listening")
        else:
            log.inf("  [listen] test mode, listening deactivated")

        def final_text(text):
            if text:
                log.inf("  [listen] final text arrived")
                self._final_text(text)

        self.listen_ready_event.set()
        while (self.recorder_active):
            self.start_listen_event.wait()

            self.start_listen_event.clear()

            if not is_testmode():
                self.recorder.text(final_text)

        self.start_listen_event.clear()

        self.recorder.shutdown()
        del self.recorder
        self.recorder = None
        gc.collect()

    def preprocess_text(self, text):
        # Remove leading whitespaces
        text = text.lstrip()

        #  Remove starting ellipses if present
        if text.startswith("..."):
            text = text[3:]

        # Remove any leading whitespaces again after ellipses removal
        text = text.lstrip()

        # Uppercase the first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text

    def is_speech_finished(self, text):
         #return False
        # Check if the result is already in the cache
        if text in self.speech_finished_cache:
            if IS_DEBUG:
                print(f"Cache hit for: '{text}'")
            return self.speech_finished_cache[text]
        
        user_prompt = (
            "Please reply with only 'c' if the following text is a complete thought (a sentence that stands on its own), "
            "or 'i' if it is not finished. Do not include any additional text in your reply. "
            "Consider a full sentence to have a clear subject, verb, and predicate or express a complete idea. "
            "Examples:\n"
            "- 'The sky is blue.' is complete (reply 'c').\n"
            "- 'When the sky' is incomplete (reply 'i').\n"
            "- 'She walked home.' is complete (reply 'c').\n"
            "- 'Because he' is incomplete (reply 'i').\n"
            f"\nText: {text}"
        )

        response = self.llm(
            messages=[{"role": "user", "content": user_prompt}],
            max_tokens=1,
            temperature=0.0,  # Set temperature to 0 for deterministic output
        )

        reply = response.choices[0].message.content.strip().lower()
        if IS_DEBUG:
            print(f"t:'{reply}'", end="", flush=True)

        result = reply == 'c'

        # Cache the result
        self.speech_finished_cache[text] = result

        return result

    def process_queue(self):
        #global  text_time_deque, abrupt_stop

        # Initialize a deque to store texts with their timestamps
        while True:
            try:
                text = self.text_queue.get(timeout=1)  # Wait for text or timeout after 1 second
            except queue.Empty:
                continue  # No text to process, continue looping

            if text is None:
                # Sentinel value to indicate thread should exit
                break

            post_speech_silence_duration = self.recorder.get_parameter("post_speech_silence_duration")
            log.inf(f"  [listen] process_queue realtime, post_speech_silence_duration: {post_speech_silence_duration}")

            text = self.preprocess_text(text)
            current_time = time.time()

            sentence_end_marks = ['.', '!', '?', '。'] 
            if text.endswith("..."):
                if not post_speech_silence_duration == mid_sentence_detection_pause:
                    self.recorder.set_parameter("post_speech_silence_duration", mid_sentence_detection_pause)
                    if IS_DEBUG: print(f"RT: post_speech_silence_duration: {post_speech_silence_duration}")
            elif text and text[-1] in sentence_end_marks and self.prev_text and self.prev_text[-1] in sentence_end_marks:
                if not post_speech_silence_duration == end_of_sentence_detection_pause:
                    self.recorder.set_parameter("post_speech_silence_duration", end_of_sentence_detection_pause)
                    if IS_DEBUG: print(f"RT: post_speech_silence_duration: {post_speech_silence_duration}")
            else:
                if not post_speech_silence_duration == unknown_sentence_detection_pause:
                    self.recorder.set_parameter("post_speech_silence_duration", unknown_sentence_detection_pause)
                    if IS_DEBUG: print(f"RT: post_speech_silence_duration: {post_speech_silence_duration}")

            self.prev_text = text
            
            import string
            transtext = text.translate(str.maketrans('', '', string.punctuation))
            
            if use_llm_sentence_end_detection and self.is_speech_finished(transtext):
                if not post_speech_silence_duration == rapid_sentence_end_detection:
                    self.recorder.set_parameter("post_speech_silence_duration", rapid_sentence_end_detection)
                    if IS_DEBUG: print(f"RT: {transtext} post_speech_silence_duration: {post_speech_silence_duration}")

            # Append the new text with its timestamp
            self.text_time_deque.append((current_time, text))

            # Remove texts older than hard_break_even_on_background_noise seconds
            while self.text_time_deque and self.text_time_deque[0][0] < current_time - hard_break_even_on_background_noise:
                self.text_time_deque.popleft()

            # Check if at least hard_break_even_on_background_noise_min_texts texts have arrived within the last hard_break_even_on_background_noise seconds
            if len(self.text_time_deque) >= hard_break_even_on_background_noise_min_texts:
                texts = [t[1] for t in self.text_time_deque]
                first_text = texts[0]
                last_text = texts[-1]

                # Compute the similarity ratio between the first and last texts
                similarity = SequenceMatcher(None, first_text, last_text).ratio()

                if similarity > hard_break_even_on_background_noise_min_similarity and len(first_text) > hard_break_even_on_background_noise_min_chars:
                    # self.abrupt_stop = True
                    self.recorder.stop()

            # Mark the task as done
            self.text_queue.task_done()


if __name__ == '__main__':
    logic = ListenLogic()
