from lingu import log, cfg, notify, wait_notify, denotify
from RealtimeTTS import (
    TextToAudioStream,
    AzureEngine,
    ElevenlabsEngine,
    SystemEngine,
    CoquiEngine,
    OpenAIEngine,
)
import logging
import os

deepspeed_installed = False
try:
    import deepspeed
    deepspeed_installed = True
    print("DeepSpeed is installed.")
except ImportError:
    print("DeepSpeed is not installed.")

language = cfg("speech", "language", default="en")
startvoice_azure = cfg(
    "speech", "startvoice_azure", default="en-US-JennyNeural")
elevenlabs_model = cfg(
    "speech", "elevenlabs_model", default="eleven_multilingual_v1")
startvoice_elevenlabs = cfg(
    "speech", "startvoice_elevenlabs", default="FunnyVoice")
startvoice_system = cfg(
    "speech", "startvoice_system", default="Katja")
model_path = cfg("speech", "xtts_model_path")

coqui_use_deepspeed = bool(cfg("speech", "coqui_use_deepspeed", default=True))

if coqui_use_deepspeed and not deepspeed_installed:
    log.err("DeepSpeed is not installed. speech/coqui_use_deepspeed=True will be ignored, DeepSpeed disabled.")
    coqui_use_deepspeed = False

# coqui default temp is 0.75, we raise to 0.9 to get it more emotional
coqui_temperature = float(cfg("speech", "coqui_temperature", default=0.9))

# coqui default lenght penalty is 1 - unchanged
coqui_length_penalty = float(cfg("speech", "coqui_length_penalty", default=1))

# coqui default repetition penalty is 5, we raise to 10
coqui_repetition_penalty = float(
    cfg("speech", "coqui_repetition_penalty", default=10))

# coqui default top_k is 50, we raise to 70
coqui_top_k = int(cfg("speech", "coqui_top_k", default=70))

# coqui default top_p is 0.85, we raise to 0.9
coqui_top_p = float(cfg("speech", "coqui_top_p", default=0.9))
coqui_pretrained = bool(cfg(
    "speech", "coqui_use_pretrained_model", default=True))


class Engines():
    def __init__(
            self,
            state,
            audio_start=None,
            audio_stop=None
    ):
        self.state = state
        self.audio_start = audio_start
        self.audio_stop = audio_stop

        self.stream: TextToAudioStream = None
        self.engine = None
        self.system_engine = None
        self.azure_engine = None
        self.elevenlabs_engine = None
        self.coqui_engine = None
        self.openai_engine = None
        self.model_path = model_path

    def get_engine(self, engine_name):

        engine_name = engine_name.lower()

        if engine_name == "azure":
            if not self.azure_engine:
                self.azure_engine = AzureEngine(
                    self.state.azure_api_key,
                    self.state.azure_region,
                    startvoice_azure,
                    rate=24,
                    pitch=10,
                )
            return self.azure_engine
        elif engine_name == "elevenlabs":
            if not self.elevenlabs_engine:
                self.elevenlabs_engine = ElevenlabsEngine(
                    self.state.elevenlabs_api_key,
                    model=elevenlabs_model,
                    stability=35,
                    clarity=80,
                    style_exxageration=20
                )
                self.elevenlabs_engine.set_voice(startvoice_elevenlabs)
            return self.elevenlabs_engine
        elif engine_name == "coqui":
            if not self.coqui_engine:
                log.dbg(f"Coqui loading language: {language}")
                print(f"specific_model: {self.state.coqui_model}")
                print(f"local_models_path: {self.model_path}")
                self.coqui_engine = CoquiEngine(
                    language=language,
                    speed=1.0,
                    specific_model=self.state.coqui_model,
                    local_models_path=self.model_path,
                    voices_path="lingu/resources",
                    voice="female.json",
                    temperature=coqui_temperature,
                    length_penalty=coqui_length_penalty,
                    repetition_penalty=coqui_repetition_penalty,
                    top_k=coqui_top_k,
                    top_p=coqui_top_p,
                    add_sentence_filter=True,
                    use_deepspeed=coqui_use_deepspeed,
                    pretrained=coqui_pretrained,
                    comma_silence_duration=0.1,
                    sentence_silence_duration=0.2,
                    default_silence_duration=0.1)
            else:
                self.set_coqui_model(self.state.coqui_model)
            return self.coqui_engine
        elif engine_name == "openai":
            if not self.openai_engine:
                self.openai_engine = OpenAIEngine()
            return self.openai_engine
        else:
            if not self.system_engine:
                self.system_engine = SystemEngine(
                    voice=startvoice_system,
                )
            return self.system_engine

    def get_engine_name_from_index(self, engine_index):
        engine_name = "system"
        if engine_index == 1:
            engine_name = "azure"
        elif engine_index == 2:
            engine_name = "elevenlabs"
        elif engine_index == 3:
            engine_name = "coqui"
        elif engine_index == 4:
            engine_name = "openai"
        return engine_name

    def get_index_from_engine_name(self, engine_name):
        engine_index = 0
        if engine_name == "azure":
            engine_index = 1
        elif engine_name == "elevenlabs":
            engine_index = 2
        elif engine_name == "coqui":
            engine_index = 3
        elif engine_name == "openai":
            engine_index = 4
        return engine_index

    def set_engine(self, engine_index):
        engine_name = self.get_engine_name_from_index(engine_index)
        self.switch_engine(engine_name)

    def switch_engine(self, engine_name):
        # import traceback
        # print("switch_engine called from:")
        # print(traceback.format_stack())

        engine_name = engine_name.lower()
        if self.engine and self.state.engine_name == engine_name:
            log.dbg(f"engine already switched to {engine_name}")
            return

        log.dbg(f"trying to switch engine to {engine_name}")

        if self.stream:
            self.stream.stop()
            self.stream = None

        self.state.engine_name = engine_name
        if engine_name == "azure":
            self.state.engine_index = 1
            self.engine = self.get_engine(engine_name)
            self.state.bottom_info = "Azure"
        elif engine_name == "elevenlabs":
            self.state.engine_index = 2
            self.engine = self.get_engine(engine_name)
            self.state.bottom_info = "Eleven"
        elif engine_name == "coqui":
            self.state.engine_index = 3
            self.engine = self.get_engine(engine_name)
            self.state.bottom_info = "Coqui"
        elif engine_name == "openai":
            self.state.engine_index = 4
            self.engine = self.get_engine(engine_name)
            self.state.bottom_info = "OpenAI"
        else:
            self.state.engine_index = 0
            self.state.bottom_info = "System"
            self.engine = self.get_engine(engine_name)
            self.state.engine_name = "system"

        if self.stream:
            self.stream.stop()
            self.stream.load_engine(self.engine)
        else:
            self.stream = TextToAudioStream(
                self.engine,
                on_audio_stream_start=self._on_audio_stream_start,
                on_audio_stream_stop=self._on_audio_stream_stop,
                level=logging.DEBUG
            )

        log.dbg("stream created")
        self.state.save()

    def _on_audio_stream_start(self):
        if self.audio_start:
            self.audio_start()

    def _on_audio_stream_stop(self):
        if self.audio_stop:
            self.audio_stop()

    def get_coqui_models(self):
        return [
            entry for entry in os.listdir(self.model_path)
            if os.path.isdir(os.path.join(self.model_path, entry))
        ]

    def set_coqui_model(self, model):
        # log.dbg(f"[speech]  set_coqui_model({model}) called from:")
        # import traceback
        # print(f"DEBUG set_coqui_model({model}) called from:")
        # print(traceback.format_stack())

        if self.coqui_engine:
            self.state.coqui_model = model
            if self.coqui_engine.specific_model != model:
                # shutdown


                
                # notify("Coqui", f"Loading model {model}.", -1, "warn", "⏳")
                # wait_notify()
                self.coqui_engine.set_model(model)
                # denotify()

    def set_coqui_speed(self, speed):
        if self.coqui_engine:
            self.coqui_engine.set_speed(speed)

    def set_voice_instance(self, engine_name, voice_instance):
        engine = self.get_engine(engine_name)

        log.inf(f"  [speech] setting voice of engine {engine_name}"
                f" to {str(voice_instance)}")
        engine.set_voice(voice_instance)

    def set_voice_parameters(self, engine_name, **voice_parameters):
        engine = self.get_engine(engine_name)

        log.inf("  [speech] setting voice parameters of engine "
                f"{engine_name} to {str(voice_parameters)}")
        engine.set_voice_parameters(**voice_parameters)

    def set_voice_parameters_by_data(self, engine_name, voice):
        if engine_name == "azure":
            self.set_voice_parameters(
                "azure",
                rate=voice["voice_rate"],
                pitch=voice["voice_pitch"]
            )
        elif engine_name == "elevenlabs":
            self.set_voice_parameters(
                "elevenlabs",
                stability=voice["voice_stability"],
                clarity=voice["voice_clarity"],
                exaggeration=voice["voice_exaggeration"]
            )
