from collections import namedtuple

DEBUG = False


class EventManager:
    def __init__(self):
        # Dictionary to hold all event listeners, with the event name as the
        # key and a list of EventListener namedtuples as the value.
        self.event_listeners = {}

    def add_listener(self, event_name, allowed_trigger_module, callback):
        """
        Registers an event listener for a specific event.

        Args:
            event_name (str): The name of the event to listen for.
            allowed_trigger_module (str): The name of the module that is
                allowed to trigger this event.
            callback (Callable): The function to be called when the event is
                triggered.
        """
        if event_name not in self.event_listeners:
            self.event_listeners[event_name] = []

        EventListener = namedtuple(
            'EventListener',
            ['callback', 'allowed_trigger_module'])
        self.event_listeners[event_name].append(
            EventListener(callback, allowed_trigger_module))

    def trigger(self, event_name, triggering_module, data=None):
        """
        Triggers an event, resulting in all registered callback functions
          being called.

        Args:
            event_name (str): The name of the event being triggered.
            triggering_module (str): The name of the module
              triggering the event.
            data (Any, optional): Data to be passed to the callback functions.

        Raises:
            Exception: If the event or the triggering module is not recognized.
        """
        if DEBUG:
            print(f"Triggering event {event_name} from module "
                  f"{triggering_module}")
        if event_name in self.event_listeners:
            for listener in self.event_listeners[event_name]:
                if DEBUG:
                    print("  Listener found triggered from module "
                          f"{listener.allowed_trigger_module}")

                if (triggering_module == listener.allowed_trigger_module or
                        listener.allowed_trigger_module == "*"):
                    if data is None:
                        listener.callback()
                    else:
                        listener.callback(data)

    def trigger_with_params(self, event_name, triggering_module, **kwargs):
        """
        Triggers an event with additional keyword arguments
          passed to callbacks.

        Args:
            event_name (str): The name of the event being triggered.
            triggering_module (str): The name of the module
              triggering the event.
            **kwargs: Keyword arguments passed to the callback functions.

        Raises:
            Exception: If the event or the triggering module is not recognized.
        """
        if event_name in self.event_listeners:
            for listener in self.event_listeners[event_name]:
                if triggering_module == listener.allowed_trigger_module:
                    listener.callback(**kwargs)


events = EventManager()
