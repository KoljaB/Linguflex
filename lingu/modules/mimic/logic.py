from lingu import log, Logic
from .state import state


class MimicLogic(Logic):
    def __init__(self):
        super().__init__()
        self.char = None
        self.voices = None
        self.add_listener("voices", "speech", self._on_voices)

    def init(self):
        self.set_char_data()
        self.ready()

    def get_char_names(self):
        return [char["name"] for char in state.chars]

    def _on_voices(self, voices):
        self.voices = voices

    def save_char(self, char, char_index):
        log.dbg(f"  saving char {char}")

        if "name" not in char or not char["name"]:
            default_name = "New char"
            counter = 1

            # Check if a char with the default name already exists
            while any(v for v in state.chars if v["name"] == default_name):
                counter += 1
                default_name = f"New char {counter}"

            char["name"] = default_name

        # If voice_index is -1, append the voice to state.voices
        if char_index == -1:
            state.chars.append(char)
            state.char_index = len(state.chars) - 1
        else:
            # Otherwise, replace the voice at the specified index
            if 0 <= char_index < len(state.chars):
                state.chars[char_index] = char
            else:
                log.dbg(f"Error: char_index {char_index} out "
                        "of range. Char not saved.")

                return

        state.save()

    def delete_char(self, char_index):
        log.dbg(f"deleting char {char_index}")

        if 0 <= char_index < len(state.chars):
            state.chars.pop(char_index)
            state.char_index = max(0, state.char_index - 1)
            if len(state.chars) == 0:
                state.char_index = -1
            state.save()
        else:
            log.err(f"Error: char_index {char_index} out of "
                    "range. Char not deleted.")

    def switch_char(self, char_index):
        log.inf(f"switching char to {char_index}")
        state.char_index = char_index

        self.set_char_data()
        state.save()

    def update_ui(self):
        self.trigger("update_ui")

    def set_char(self, char_name):
        log.inf(f"setting char to {char_name}")

        for i, char in enumerate(state.chars):
            if char["name"] == char_name:
                state.char_index = i
                break

        self.set_char_data()
        state.save()
        self.update_ui()

    def set_char_data(self):
        if state.char_index == -1 or state.char_index >= len(state.chars):
            log.dbg("can not set_char_data char index out of range")
            return False

        self.char = state.chars[state.char_index]
        char_prompt = self.char["prompt"]
        char_voice = self.char["voice"]

        if char_voice:
            self.trigger("set_voice", char_voice)
        self.trigger("set_prompt", char_prompt)

        return True


logic = MimicLogic()
