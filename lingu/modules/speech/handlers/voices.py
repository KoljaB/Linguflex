from lingu import log, events
from .engines import Engines
from RealtimeTTS import (
    AzureVoice,
    ElevenlabsVoice,
    SystemVoice,
    CoquiVoice,
    OpenAIVoice,
)


class Voices():
    def __init__(
            self,
            logic,
            engines: Engines,
            state):

        self.logic = logic
        self.state = state
        self.engines = engines

        self.voice_cache = {}

    def get_voices(self, engine_name):
        if engine_name in self.voice_cache:
            return self.voice_cache[engine_name]

        engine = self.engines.get_engine(engine_name)
        voices = engine.get_voices()

        log.dbg(f"Engine {engine_name} has voices:")
        for voice in voices:
            log.dbg(f"  {voice}")

        self.voice_cache[engine_name] = voices
        return voices

    def send_voices(self):
        events.trigger("voices", "speech", self.state.voices)

    def save_voice(self, voice, voice_index):
        log.dbg(f"  saving voice {voice} to index {voice_index}")

        voice_name = voice["name"]
        if not voice_name or voice_index == -1:
            voice_name = "Unnamed Voice"
            voice["name"] = voice_name

        name_exists = any(
            v for v in self.state.voices
            if v["name"] == voice_name
        )

        if voice_index == -1 and name_exists:
            counter = 2
            default_name = f"{voice_name} {counter}"

            # Check if a voice with the default name already exists
            while any(
                v for v in self.state.voices
                if v["name"] == default_name
            ):
                counter += 1
                default_name = f"{voice_name} {counter}"

            voice["name"] = default_name

        # If voice_index is -1, append the voice to state.voices
        if voice_index == -1:
            self.state.voices.append(voice)
            self.state.voice_index = len(self.state.voices) - 1
        else:
            # Otherwise, replace the voice at the specified index
            if 0 <= voice_index < len(self.state.voices):
                self.state.voices[voice_index] = voice
            else:
                log.dbg(f"Error: voice_index {voice_index} out "
                        "of range. Voice not saved.")

                return

        self.state.save()
        self.send_voices()

    def delete_voice(self, voice_index):
        log.dbg(f"deleting voice {voice_index}")

        if 0 <= voice_index < len(self.state.voices):
            self.state.voices.pop(voice_index)
            self.state.voice_index = max(0, self.state.voice_index - 1)
            if len(self.state.voices) == 0:
                self.state.voice_index = -1
            self.state.save()
        else:
            log.err(f"Error: voice_index {voice_index} out of "
                    "range. Voice not deleted.")
        self.send_voices()

    def mimic_set_voice(self, voice):
        for i, state_voice in enumerate(self.state.voices):
            if state_voice["name"] == voice["name"]:
                self.switch_voice(i)
                break

    def set_voice(self, voice):
        voice_instance = None
        if voice["engine"] == "system":
            voice_instance = SystemVoice(
                voice["voice_name"],
                voice["voice_id"],
            )
        elif voice["engine"] == "azure":
            voice_instance = AzureVoice(
                voice["voice_full_name"],
                voice["voice_locale"],
                voice["voice_gender"],
            )
        elif voice["engine"] == "elevenlabs":
            voice_instance = ElevenlabsVoice(
                voice["voice_name"],
                voice["voice_id"],
                voice["voice_category"],
                voice["voice_description"],
                voice["voice_labels"],
            )
        elif voice["engine"] == "openai":
            voice_instance = OpenAIVoice(
                voice["voice_name"],
            )
        elif voice["engine"] == "coqui":
            if "voice_name" in voice:
                voice_instance = CoquiVoice(
                    voice["voice_name"],
                )
            else:
                voice_instance = CoquiVoice(
                    "female.json"
                )

        if voice_instance:
            self.engines.set_voice_instance(voice["engine"], voice_instance)

    def set_voice_data(self):
        if (
            self.state.voice_index == -1
            or self.state.voice_index >= len(self.state.voices)
        ):
            log.dbg("can not set_voice_data voice index out of range")
            return False

        voice = self.state.voices[self.state.voice_index]

        if voice["engine"] == "coqui":
            if "model" in voice:
                self.state.coqui_model = voice["model"]
            else:
                self.state.coqui_model = "v2.0.2"

        self.engines.switch_engine(voice["engine"])

        self.set_voice(voice)

        # set rvc enabled, pitch and model
        self.state.rvc_enabled = voice.get("rvc_enabled", False)
        self.state.rvc_pitch = voice.get("rvc_pitch", 0)
        self.state.rvc_model = voice.get("rvc_model", "")

        self.engines.set_voice_parameters_by_data(
            self.state.engine_name,
            voice)
        return True

    def switch_voice(self, voice_index):
        log.inf(f"switching voice to {voice_index}")
        self.state.voice_index = voice_index

        self.set_voice_data()
        self.logic.update_ui()
        self.state.save()
