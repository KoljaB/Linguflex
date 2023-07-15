from core import log, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase
from pydantic import Field
import pyperclip

class copy_to_clipboard(LinguFlexBase):
    "Copies the given content into the windows clipboard (copy)"
    content: str = Field(..., description="Content to copy or write into clipboard.")

    def execute(self):
        try:
            log(DEBUG_LEVEL_MAX, f"  [clipboard] writing content: {self.content}")
            pyperclip.copy(self.content)
            return {'status': 'success', 'message': 'Content copied to clipboard successfully.'}
        except Exception as e:
            log(DEBUG_LEVEL_ERR, f"  [clipboard] Error copying content to clipboard: {str(e)}")
            return {'status': 'error', 'message': str(e)}

class paste_from_clipboard(LinguFlexBase):
    "Returns the content of the windows clipboard (paste)"

    def execute(self):
        try:
            clipboard_content = pyperclip.paste()
            log(DEBUG_LEVEL_MAX, f"  [clipboard] retrieved content: {clipboard_content}")
            return {'status': 'success', 'content': clipboard_content}
        except Exception as e:
            log(DEBUG_LEVEL_ERR, f"  [clipboard] Error retrieving content from clipboard: {str(e)}")
            return {'status': 'error', 'message': str(e)}