"""
Brain Module

- responsible for switching and configuring LLMs
- handles the clipboard

"""

from lingu import log, Populatable
from pydantic import Field
import pyperclip


# # This is out data module whose fields will be populated by AI
# class SwitchLanguageModel(Populatable):
#     "Select between GPT 4, GPT 3.5 and local large language model"

#     # define the fields the AI can use to populate the module
#     model: str = Field(None, description="Must be either \"GPT 4\", \"GPT 3.5\" or \"Local\"")

#     # the method that gets called after the AI has populated the module
#     def on_populated(self):
#         return logic.switch_language_model_to(self.model)


class PutContentToClipboard(Populatable):
    "Puts the given content into the windows clipboard (copy)"
    content: str = Field(
        ...,
        description="Content to copy or write into clipboard.")

    def on_populated(self):
        try:
            log.dbg(f"  [clipboard] writing content: {self.content}")
            pyperclip.copy(self.content)
            return {'status': 'success',
                    'message': 'Content copied to clipboard successfully.'}
        except Exception as e:
            log.err(f"  [clipboard] Error copying content to clipboard: {str(e)}")
            return {'status': 'error', 'message': str(e)}


class LookIntoTheClipboard(Populatable):
    """
    Returns the content of the windows clipboard (paste).
    Call when asked to look into the clipboard.
    """

    def on_populated(self):
        try:
            clipboard_content = pyperclip.paste()
            log.inf(f"  [clipboard] retrieved content: {clipboard_content}")
            return {'status': 'success',
                    'clipboard content': clipboard_content}
        except Exception as e:
            log.err("  [clipboard] Error retrieving content from clipboard: "
                    f"{str(e)}")
            return {'status': 'error', 'message': str(e)}
