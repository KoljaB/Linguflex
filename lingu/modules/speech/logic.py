from lingu import log, cfg, Logic, RealtimeRVC
from .state import state
from .handlers.feed2stream import BufferStream
from .handlers.engines import Engines
from .handlers.voices import Voices
from .handlers.resample import Resampler
import numpy as np
import threading
import os
import resampy
from scipy.signal import butter, lfilter

force_first_fragment_after_words = \
    int(cfg("speech", "force_first_fragment_after_words", default=12))

# speed-optimized:
# min_sentence_length = 5
# min_first_fragment_length = 5
# fast_sentence_fragment = True

# quality-optimized:
min_sentence_length = 25
min_first_fragment_length = 25
fast_sentence_fragment = False


class SpeechLogic(Logic):
    """
    SpeechLogic is a class that manages speech synthesis in the assistant.
    """
    def init(self):
        """
        Initialize the SpeechLogic class.

        This method sets up the necessary components for speech synthesis,
        including voice selection, engine setup, and event listeners.

        """
        # Flag to indicate if the speech logic is running.
        self.is_running = True
        self.resampler = Resampler(16000, 48000)  # values get changed later

        # RealtimeRVC object for real-time voice cloning.
        self.rvc = RealtimeRVC(
            self.rvc_stop,
            self.rvc_yield_chunk_callback
        )
        self.set_rvc_enabled(state.rvc_enabled)
        self.muted = False
        self.playout_yielded = False

        # Read environment variables for Azure and Elevenlabs API keys.
        if os.environ.get("AZURE_SPEECH_KEY"):
            state.azure_api_key = os.environ.get("AZURE_SPEECH_KEY")
        if os.environ.get("AZURE_SPEECH_REGION"):
            state.azure_region = os.environ.get("AZURE_SPEECH_REGION")
        if os.environ.get("ELEVENLABS_API_KEY"):
            state.elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")

        # Initialize the engines and voices.
        self.engines = Engines(
            state,
            audio_start=self.audio_start,
            audio_stop=self.audio_stop,
        )
        self.voices = Voices(
            self,
            self.engines,
            state)
        self.voices.send_voices()
        if state.voice_index >= 0 and state.voice_index < len(state.voices):
            state.top_info = state.voices[state.voice_index]["name"]

        # Add event listeners.
        self.add_listener("assistant_chunk",
                          "brain",
                          self.play_text)
        self.add_listener("assistant_text_start",
                          "brain",
                          self.assistant_text_start)
        self.add_listener("assistant_text_complete",
                          "brain",
                          self.assistant_text_complete)
        self.add_listener("set_voice",
                          "mimic",
                          self.voices.mimic_set_voice)
        self.add_listener(
            "escape_key_pressed",
            "*",
            self.abort_speech_immediately)
        self.add_listener(
            "volume_interrupt",
            "*",
            self.abort_speech_immediately)
        self.add_listener(
            "client_connected",
            "server",
            self._yield_playout)
        self.add_listener(
            "client_disconnected",
            "server",
            self._stop_yield_playout)
        # Create buffer for output text stream.
        self.text_stream = BufferStream()

        # Initialize voice and engine
        if not self.voices.set_voice_data():
            # no voice defined yet, start with last selected engine
            # (fetch from state)
            log.dbg("  [speech] starting with engine "
                    f"{state.engine_name}")
            self.engines.switch_engine(state.engine_name)
            self.voices.select_first_voice(self.engines.engine)

        self.trigger("speech_ready")

        self.ready()

    def _yield_playout(self):
        self.state.set_text("🌐")
        log.inf("  [speech] client connected, disabling sound output")
        self.playout_yielded = True

    def _stop_yield_playout(self):
        self.state.set_text("")
        log.inf("  [speech] client disconnected, enabling sound output")
        self.playout_yielded = False

    def yield_chunk_callback(self, chunk):

        _, _, sample_rate = self.engines.engine.get_stream_info()
        self.resampler.set_sample_rate(sample_rate, 48000)
        np_data = np.frombuffer(chunk, dtype=np.int16)
        np_resampled_data = self.resampler.resample(np_data)
        chunk = np_resampled_data.astype(np.float32) / 32767.0
        chunk = chunk.newbyteorder('<')  # Force little-endian
        chunk = chunk.tobytes()
        self.trigger("audio_chunk", chunk)

    def resample_float32_to_float32(
            self,
            chunk,
            sample_rate,
            target_sample_rate):
        """
        We need to resample from rvc engine sample rate to 48 kHz.
        Otherwise speech output on browser client won't work.
        """

        # Assume chunk is a bytes object containing float32 data
        audio_data = np.frombuffer(chunk, dtype=np.float32)

        # # Create a low-pass filter
        # nyquist_rate = sample_rate / 2
        # cutoff_freq = nyquist_rate * 0.9  # Adjust the cutoff frequency as needed
        # order = 6  # Adjust the filter order as needed
        # b, a = butter(order, cutoff_freq / nyquist_rate, btype='low', analog=False)

        # # Apply the low-pass filter to the audio data
        # filtered_audio = lfilter(b, a, audio_data)
        # audio_data = filtered_audio

        # Resample the audio
        resampled_audio = resampy.resample(audio_data, sample_rate, target_sample_rate)
        audio_data = resampled_audio

        # The data is already in float32, scale it to [-1, 1]
        audio_data = audio_data.astype(np.float32)
        audio_data = audio_data.newbyteorder('<')  # Force little-endian if needed

        chunk = audio_data.tobytes()

        return chunk

    def rvc_yield_chunk_callback(self, chunk):
        float32_size = 4  # bytes per float32
        num_floats_per_chunk = 2048 // float32_size  # 512 float32 elements per sub-chunk

        # Calculate the total number of float32 elements in the chunk
        total_floats = len(chunk) // float32_size
        
        # Calculate the number of full sub-chunks that can be extracted
        num_full_sub_chunks = total_floats // num_floats_per_chunk
        
        # Iterate over each full sub-chunk and trigger an event
        for i in range(num_full_sub_chunks):
            start_index = i * num_floats_per_chunk * float32_size
            end_index = start_index + num_floats_per_chunk * float32_size
            sub_chunk = chunk[start_index:end_index]
            self.trigger("rvc_audio_chunk", sub_chunk)
        
        # Handle any remaining data that's less than a full sub-chunk
        remaining_data_start = num_full_sub_chunks * num_floats_per_chunk * float32_size
        if remaining_data_start < len(chunk):
            remaining_data = chunk[remaining_data_start:]        
            self.trigger("rvc_audio_chunk", remaining_data)
        # self.trigger("rvc_audio_chunk", chunk)
        # Determine the size of each chunk in bytes
        # chunk_size = 2048
        
        # # Calculate the number of full chunks that can be extracted from the input
        # num_full_chunks = len(chunk) // chunk_size
        
        # # Iterate over each full chunk and trigger an event
        # for i in range(num_full_chunks):
        #     start = i * chunk_size
        #     end = start + chunk_size
        #     sub_chunk = chunk[start:end]
        #     self.trigger("rvc_audio_chunk", sub_chunk)
        
        # # Optional: Handle any remaining data that's less than a full chunk
        # remaining_data_start = num_full_chunks * chunk_size
        # if remaining_data_start < len(chunk):
        #     remaining_data = chunk[remaining_data_start:]
        #     self.trigger("rvc_audio_chunk", remaining_data)
            # Here you could either store this and wait until you accumulate enough for a full chunk,
            # or decide to send it as is (may not be desirable depending on your use case).
            # For example:
            # self.trigger("rvc_audio_chunk", remaining_data)
    # def rvc_yield_chunk_callback(self, chunk):

    #     self.trigger("rvc_audio_chunk", chunk)

        #chunk = self.resample_float32_to_float32(chunk, 40000, 48000)
        # self.resampler.set_sample_rate(40000, 48000)
        # np_data = np.frombuffer(chunk, dtype=np.float32)
        # # Scale float32 data to int16 range
        # np_data_int16 = (np_data * 32767).astype(np.int16)
        # np_resampled_data = self.resampler.resample(np_data_int16)
        # chunk = np_resampled_data.astype(np.float32) / 32767.0
        # chunk = chunk.newbyteorder('<')  # Force little-endian
        # chunk = chunk.tobytes()
        # self.trigger("audio_chunk", chunk)

    def post_init_processing(self):
        if not state.engine_name == "coqui":
            return

        warmup = bool(cfg("speech", "warmup", default=False))
        if warmup:
            warmup_text = cfg("speech", "warmup_text", default="Hi")
            warmup_muted = bool(cfg("speech", "warmup_muted", default=False))

            # delayed execute warmup
            threading.Timer(2, self.test_voice, args=[warmup_text, warmup_muted]).start()

    def assistant_text_start(self):
        """
        Handle the start of assistant text input.

        This method is called when the assistant starts processing text input.
        It initializes the text stream for speech synthesis.

        """
        if state.rvc_enabled:
            self.rvc.init()
        self.text_stream = BufferStream()

    def assistant_text_complete(self, _):
        """
        Handle the completion of assistant text input.

        This method is called when the assistant completes processing text.
        It stops the text stream for speech synthesis.

        """
        self.text_stream.stop()

    def play_text(self, text, muted=False):
        """
        Play synthesized speech for the given text.

        Args:
            text (str): The text to be synthesized and played.

        """
        # print(f"Playing text: {text}, muted: {muted}")
        self.muted = muted
        self.text_stream.add(text)
       

        if not self.engines.stream.is_playing():
            self.engines.stream.feed(self.text_stream.gen())
            if state.rvc_enabled:
                self.rvc.chunk_callback_only = self.playout_yielded
                self.engines.stream.play_async(
                    fast_sentence_fragment=fast_sentence_fragment,
                    minimum_sentence_length=min_sentence_length,
                    minimum_first_fragment_length=min_first_fragment_length,
                    # log_synthesized_text=True,
                    on_audio_chunk=self.feed_to_rvc,
                    context_size=4,
                    muted=True,
                    sentence_fragment_delimiters=".?!;:,\n()[]{}。-“”„”—…/|《》¡¿\"",
                    force_first_fragment_after_words=force_first_fragment_after_words,
                    )
            else: 
                if not self.playout_yielded:
                    # log.inf(f"  [speech] normal playing text: {text}, 'muted': {muted}")
                    self.engines.stream.play_async(
                        fast_sentence_fragment=fast_sentence_fragment,
                        minimum_sentence_length=min_sentence_length,
                        minimum_first_fragment_length=min_first_fragment_length,
                        # log_synthesized_text=True,
                        context_size=4,
                        muted=muted,
                        sentence_fragment_delimiters=".?!;:,\n()[]{}。-“”„”—…/|《》¡¿\"",
                        force_first_fragment_after_words=force_first_fragment_after_words,
                        )
                else:
                    # log.inf(f"  [speech] yield_chunk_callback playing text 'text': {text}")
                    self.engines.stream.play_async(
                        fast_sentence_fragment=fast_sentence_fragment,
                        minimum_sentence_length=min_sentence_length,
                        minimum_first_fragment_length=min_first_fragment_length,
                        on_audio_chunk=self.yield_chunk_callback,
                        context_size=4,
                        muted=True,
                        sentence_fragment_delimiters=".?!;:,\n()[]{}。-“”„”—…/|《》¡¿\"",
                        force_first_fragment_after_words=force_first_fragment_after_words,
                        )
        
    def test_voice(self, text, muted=False):
        """
        Test a voice by synthesizing and playing the given text.

        Args:
            text (str): The text to be synthesized and played for testing.

        """
        print(f"Testing voice: {text}, muted: {muted}")
        self.trigger("stop_recorder")
        print("self.state.set_active(True)")
        self.state.set_active(True)

        self.text_stream = BufferStream()
        if state.rvc_enabled:
            self.rvc.init()

        self.play_text(text, muted)
        self.text_stream.stop()

    def audio_start(self):
        """
        Handle the start of audio playback.

        This method is called when audio playback begins.

        """
        self.trigger("audio_stream_start")
        self.state.set_active(True)

    def audio_stop(self):
        """
        Handle the stop of audio playback.

        This method is called when audio playback stops.
        If Realtime Voice Cloning (RVC) is not enabled,
        it triggers the stop of audio streaming. Otherwise,
        the stop of audio streaming is handled by the RVC.
        """
        if not state.rvc_enabled:
            self.trigger("audio_stream_stop")
            self.state.set_active(False)
        else:
            self.rvc.feed_finished()

    def update_ui(self):
        """
        Update the user interface with the current voice information.

        This method updates the user interface to display
        the current voice information.

        """
        self.trigger("update_ui")

    def feed_to_rvc(self, chunk):
        """
        Feed synthesized speech to RealtimeRVC for voice cloning.

        Args:
            text (str): The synthesized speech text to be fed to RealtimeRVC.

        """
        if not self.muted:
            _, _, sample_rate = self.engines.engine.get_stream_info()
            if self.playout_yielded:
                # yield up to 60000 ?
                # print("yielding chunk to rvc")
                self.rvc.feed(chunk, sample_rate, 48000)
            else:
                self.rvc.feed(chunk, sample_rate)

    def rvc_stop(self):
        """
        RealtimeRVC stopped audio.

        RealtimeRVC stopped audio streaming. This method triggers
        the stop of audio streaming and sets speech module to inactive.
        """
        self.trigger("audio_stream_stop")
        self.state.set_active(False)

    def set_rvc_enabled(self, enabled):
        """
        Set the Realtime Voice Cloning (RVC) enabled/disabled state.

        Args:
            enabled (bool): A boolean indicating whether RVC should
              be enabled or disabled.
        """
        state.rvc_enabled = enabled

        if enabled and not self.rvc.started:
            log.dbg("Starting Realtime Voice Cloning (enabled)")
            if state.rvc_model:
                self.rvc.start(state.rvc_model)
            else:
                log.dbg("Retrieving models")
                models = self.rvc.get_models()
                if models:
                    state.rvc_model = models[0]
                    log.dbg("Starting first model")
                    self.rvc.start(state.rvc_model)

    def set_rvc_pitch(self, pitch):
        """
        Set the pitch for Realtime Voice Cloning.

        Args:
            pitch: The pitch value to set for Realtime Voice Cloning.

        """
        if self.rvc:
            self.rvc.set_pitch(pitch)

    def get_rvc_models(self):
        """
        Get the available Realtime Voice Cloning models.

        Returns:
            A list of available Realtime Voice Cloning models.
        """
        return self.rvc.get_models()

    def set_rvc_model(self, model_name):
        """
        Set the Realtime Voice Cloning model.

        Args:
            model_name: The name of the Realtime Voice Cloning model to set.
        """
        state.rvc_model = model_name
        log.dbg(f"setting rvc model to {model_name}")
        state.save()
        self.rvc.set_model(model_name)

    def abort_speech_immediately(self):
        """
        Abort speech immediately.

        This method aborts speech immediately by stopping the audio stream.

        """

        if self.engines and self.engines.stream:
            if self.engines.stream.is_playing():
                self.engines.stream.stop()

            if self.rvc and self.rvc.is_playing():
                self.rvc.stop()


logic = SpeechLogic()
