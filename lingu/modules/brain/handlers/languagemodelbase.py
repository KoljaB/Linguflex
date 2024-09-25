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

    def generate(self, user_text, messages, functions=None):
        raise NotImplementedError("The get_stream_info method must be implemented by the derived class.")

    def generate_image(self, messages, prompt: str, image_path: str, image_source: str):
        unavail_str = "Image processing is not yet available for this llm provider, please switch to openai or ollama."
        for chunk in unavail_str:
            yield chunk

    def set_model(self, model_name):
        raise NotImplementedError("The set_model method must be implemented by the derived class.")

    def add_tools_to_history(self, tools, history):
        raise NotImplementedError("The add_executed_tools method must be implemented by the derived class.")        