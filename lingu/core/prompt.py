from lingu import cfg
import datetime

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

        self.reset()
        self.set_base_prompt(base_prompt)

    def set_base_prompt(self, prompt):
        """
        Set the base prompt and reset the prompt construction.

        Args:
            prompt (str): The base prompt string to set.
        """
        self.init_prompt = prompt
        self.start()

    def reset(self):
        self.pre_normal_prompts = []
        self.pre_prio_prompts = []

    def start(self):
        """
        Reset the prompt construction process and append pre-prompts.
        """
        self.normal_prompts = self.pre_normal_prompts.copy()
        self.prio_prompts = self.pre_prio_prompts.copy()
        self.prompt = self.init_prompt

    def pre_add(self, text, prioritize=False):
        if not text:
            return
        if text in self.pre_normal_prompts or text in self.pre_prio_prompts:
            return
        if prioritize:
            self.pre_prio_prompts.append(text)
        else:
            self.pre_normal_prompts.append(text)

    def add(self, text, prioritize=False):
        """
        Add a new prompt component.

        Args:
            text (str): The prompt text to add.
            prioritize (bool): If True, the prompt is
                added to priority prompts.
        """
        if not text:
            return
        if text in self.normal_prompts or text in self.prio_prompts:
            return
        if prioritize:
            self.prio_prompts.append(text)
        else:
            self.normal_prompts.append(text)

    def build_prompt(self):
        prio_prompt_str = " ".join(self.prio_prompts)

        # Strip any leading or trailing whitespace
        # from the priority prompt string
        prio_prompt_str = prio_prompt_str.strip()

        # Add a space at the end if the init prompt string is not empty
        init_prompt = self.init_prompt
        if init_prompt:
            init_prompt = init_prompt.rstrip() + " "

        # Initialize the final prompt with the priority prompt
        # and the initial prompt
        prompt = init_prompt + prio_prompt_str

        # Initialize the normal prompt string by
        # joining the normal prompts list
        normal_prompt_str = " ".join(self.normal_prompts)

        # Strip any leading or trailing whitespace
        # from the normal prompt string
        normal_prompt_str = normal_prompt_str.strip()

        # Add the normal prompt string to the final prompt if it's not empty
        if normal_prompt_str:
            prompt += " " + normal_prompt_str

        # Strip any leading or trailing whitespace from the final prompt
        prompt = prompt.strip()

        # Return the final prompt
        return prompt

    def get(self):
        """
        Construct and return the final prompt string.

        Returns:
            str: The constructed prompt string.
        """
        return self.build_prompt()

    def system_prompt(self):
        """
        Constructs and returns the system prompt string with the current date,
        including the day of the week.

        Returns:
            str: The system prompt with the current date
              and day of the week appended.
        """
        # Retrieve the existing prompt content, if any.
        prompt_content = self.get() if self.get() else ""

        # Append a newline for formatting, if the prompt has content.
        if prompt_content:
            prompt_content += "\n\n"

        # Get the current date, day, and time
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%A, %Y-%m-%d %H:%M:%S")

        # Construct the prompt content
        prompt_content += f"Current date and time: {formatted_datetime}"

        return prompt_content


prompt = Prompt()
