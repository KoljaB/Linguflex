from lingu import log, Logic, RealtimeRVC
from .state import state
from .handlers.feed2stream import BufferStream
from .handlers.engines import Engines
from .handlers.voices import Voices
import os


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

        # RealtimeRVC object for real-time voice cloning.
        self.rvc = RealtimeRVC(self.rvc_stop)
        self.set_rvc_enabled(state.rvc_enabled)

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

        # Create buffer for output text stream.
        self.text_stream = BufferStream()

        # Initialize voice and engine
        if not self.voices.set_voice_data():
            log.dbg("  [speech] starting with engine "
                    f"{state.engine_name}")
            self.engines.switch_engine(state.engine_name)

        self.trigger("speech_ready")
        self.ready()

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

    def play_text(self, text):
        """
        Play synthesized speech for the given text.

        Args:
            text (str): The text to be synthesized and played.

        """
        self.text_stream.add(text)
        self.engines.stream.feed(self.text_stream.gen())

        if not self.engines.stream.is_playing():
            if state.rvc_enabled:
                self.engines.stream.play_async(
                    fast_sentence_fragment=True,
                    minimum_sentence_length=10,
                    minimum_first_fragment_length=10,
                    on_audio_chunk=self.feed_to_rvc,
                    context_size=8,
                    muted=True)
            else:
                self.engines.stream.play_async(
                    fast_sentence_fragment=True,
                    minimum_sentence_length=10,
                    minimum_first_fragment_length=10,
                    context_size=8)

    def test_voice(self, text):
        """
        Test a voice by synthesizing and playing the given text.

        Args:
            text (str): The text to be synthesized and played for testing.

        """
        self.trigger("stop_recorder")
        self.state.set_active(True)

        self.text_stream = BufferStream()
        if state.rvc_enabled:
            self.rvc.init()

        self.play_text(text)
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
            self.rvc.stop()

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
        _, _, sample_rate = self.engines.engine.get_stream_info()
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
            # print("Starting Realtime Voice Cloning (enabled)")
            if state.rvc_model:
                self.rvc.start(state.rvc_model)
            else:
                models = self.rvc.get_models()
                if models:
                    state.rvc_model = models[0]
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


logic = SpeechLogic()
