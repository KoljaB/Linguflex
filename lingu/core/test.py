from .events import events
from .arguments import get_argument
from .log import log
import time

def is_testmode():
    return get_argument('runtests') or get_argument('tests') or get_argument('test') 

class Test():
    """
    Base class for module tests 

    This class offers functionality to control linguflex
    "from the outside", so we have a set of methods we can
    call to "automate" workflows within lingu for tests.
    """

    def __init__(self):
        """
        Initializes the Test.
        """
        self.module_name = "Unknown"

        self.assistant_text = ""

        events.add_listener(
            "assistant_text_complete",
            "brain",
             self.update_assistant_text)
        
    def update_assistant_text(self, text):
        """
        Update the assistant_text attribute.
        """
        self.assistant_text = text
    
    def trigger(self, module_name: str, event_name: str, data=None):
        """Triggers an event with optional data.

        Args:
            event_name (str): The name of the event to trigger.
            data: Optional data to pass with the event.

        Returns:
            The result of the event trigger.
        """
        if event_name != "recorded_chunk":
            print(f"events.trigger({event_name}, {module_name}, {data})")
        return events.trigger(event_name, module_name, data)
    
    def trigger_with_params(self,  module_name: str, event_name: str, **kwargs):
        """Triggers an event with named parameters.

        Args:
            event_name (str): The name of the event to trigger.
            **kwargs: Arbitrary keyword arguments to pass with the event.

        Returns:
            The result of the event trigger.
        """
        return events.trigger_with_params(
            event_name,
            module_name,
            **kwargs
        )   
 
    def user(self, request_text, delay=0.2):
        self.assistant_text = ""
        log.inf(f"  [test] mock user request: {request_text}")

        words = request_text.split()
        for i in range(1, len(words) + 1):
            text_so_far = ' '.join(words[:i])
            print(text_so_far)
            self.trigger("listen", "user_text", text_so_far)
            time.sleep(delay)

        self.trigger("listen", "user_text_complete", request_text)

        while self.assistant_text == "":
            time.sleep(0.01)

        log.inf(f"  [test] assistant answered: {self.assistant_text}")
        return self.assistant_text

    def clear_history(self):
        log.inf(f"  [test] clearing conversation history")
