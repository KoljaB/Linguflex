from .linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR

class Request():
    def __init__(self) -> None:        
        self.functions = [] 
        self.function_call = None 
        self.function_name_execute = None 
        self.function_name_answer = None
        self.function_arguments = None
        self.function_content = None

        self.input = None 
        self.audio = None 
        self.output = None
        self.prompt = None
        self.user_id = None 

        # The `initialize_request` attribute can store another request to be processed after this one.
        # This enables request chaining and is utilized by the `new` and `function_answer` methods.
        self.initialize_request = None 

    def new(self, prompt = '', input = ''): 
        request = Request()
        request.user_id = self.user_id
        request.input = input or self.input
        request.original_input = self.input
        request.skip_input = True
        self.initialize_request = request
        if prompt is not None:
            request.add_prompt(prompt)
        return request

    def function_answer(self, function_name: str, function_content: str): 
        request = self.new()
        request.function_name_answer = function_name
        request.function_content = function_content
        return request     

    def add_prompt(self, text: str):
        if text is None: return
        text = text.strip()
        if not len(text): return

        if self.prompt is not None:
            if not hasattr(self, 'prompt_added'):
                error_msg = 'Direct assignment to the "prompt" attribute of the Request class is discouraged. Use the "add_prompt" method to ensure proper handling of prompts.'
                log(DEBUG_LEVEL_MIN, f'  WARNING: {error_msg} Content of prompt: {self.prompt}')
                raise ValueError(error_msg)

        if self.prompt is None:
            self.prompt = ''

        if text and len(text) and not text in self.prompt:
            self.prompt = f'{self.prompt or ""} {text}'.strip()

        if not self.prompt is None and not len(self.prompt):
            self.prompt = None

        if not self.prompt is None:
            self.prompt_added = True