class LLM_Base():
    def __init__(self):
        self.tools = None

    def set_tools(self, tools):
        self.tools = tools

    def get_user_message(self, messages):
        """
        Retrieve the content of the last message sent by the user from a list of messages.

        Args:
        messages (list): A list of message dictionaries.

        Returns:
        str: The content of the last user message.
        """
        for message in reversed(messages):
            if message["role"] == "user":
                return message, message["content"]
        return None, None

    def set_temperature(self, temperature):
        raise NotImplementedError("The set_temperature method must be implemented by the derived class.")

    def generate(self, messages, functions=None):
        raise NotImplementedError("The get_stream_info method must be implemented by the derived class.")

    def generate_image(self, messages):
        raise NotImplementedError("The generate_image method must be implemented by the derived class.")

    # def get_execution_function(self):
    #     raise NotImplementedError("The get_execution_function method must be implemented by the derived class.")

    def set_model(self, model_name):
        raise NotImplementedError("The set_model method must be implemented by the derived class.")