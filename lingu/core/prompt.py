from lingu import cfg

BASE_PROMPT = cfg("prompt")


class Prompt():
    """
    A class to manage and construct a complex prompt
    from individual components.

    Attributes:
        init_prompt (str): The base prompt to start with.
        normal_prompts (list[str]): A list of additional prompt strings.
        prio_prompts (list[str]): A list of priority prompt strings.
        prompt (str): The final constructed prompt.

    Methods:
        __init__(base_prompt): Initializes the class with a base prompt.
        set_base_prompt(prompt): Sets the base prompt
          and resets the prompt construction.
        start(): Resets the prompt construction process.
        add(text, prioritize=False): Adds a new prompt component.
        get(): Constructs and returns the final prompt string.
    """
    def __init__(self, base_prompt=BASE_PROMPT):
        """
        Initialize the Prompt class with a base prompt.

        Args:
            base_prompt (str): The base prompt to start with.
        """
        super().__init__()

        self.set_base_prompt(base_prompt)
        self.start()

    def set_base_prompt(self, prompt):
        """
        Set the base prompt and reset the prompt construction.

        Args:
            prompt (str): The base prompt string to set.
        """
        self.init_prompt = prompt
        self.start()

    def start(self):
        """
        Reset the prompt construction process.
        """
        self.normal_prompts = []
        self.prio_prompts = []
        self.prompt = self.init_prompt

    def add(self, text, prioritize=False):
        """
        Add a new prompt component.

        Args:
            text (str): The prompt text to add.
            prioritize (bool): If True, the prompt is added to priority prompts.
        """
        if not text:
            return
        if text in self.normal_prompts or text in self.prio_prompts:
            return
        if prioritize:
            self.prio_prompts.append(text)
        else:
            self.normal_prompts.append(text)

    def get(self):
        """
        Construct and return the final prompt string.

        Returns:
            str: The constructed prompt string.
        """
        prio_prompt_str = " ".join(self.prio_prompts)
        prio_prompt_str = prio_prompt_str.strip()
        if prio_prompt_str:
            prio_prompt_str += " "
        prompt = prio_prompt_str + self.init_prompt
        normal_prompt_str = " ".join(self.normal_prompts)
        normal_prompt_str = normal_prompt_str.strip()
        if normal_prompt_str:
            prompt += " " + normal_prompt_str
        prompt = prompt.strip()
        return prompt


prompt = Prompt()
