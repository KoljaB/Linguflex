DEFAULT_USER = 'DefaultUser'

class LinguFlexMessage():
    def __init__(self) -> None:        
        self.audio = None # path to audio data
        self.input = None # input text
        self.original_input = None # needed to smuggle through user input in chained messages by modules
        self.skip_input = False # request from module to not process next input (LinguFlexMessages raised by modules would not want this)
        self.user_id = DEFAULT_USER # user identification for client-individual history etc
        self.prompt = '' # system prompt to instruct llm
        self.llm = '' # preferred llm model to use
        self.prompt_end = '' # information to add at last
        self.ignore_actions = '' # modules to ignore action
        self.character = ''
        self.ignore_character_prompt = False
        self.clone_last_user_input = False
        self.no_history = False
        self.raise_actions = '' # modules to allow actions for llm        
        self.output = None # raw llm output text
        self.output_user = None # output optimized for user
        self.original_output = None # needed to smuggle through assistant output in chained messages by modules
        self.original_output_user = None # needed to smuggle through assistant output in chained messages by modules
        self.remove_from_history = False # request from module to remove the last message from history (LinguFlexMessages raised by modules would not want this)
        self.skip_output = False # request from module to not communicate answer to user
        self.history = '' # conversation history
        self.tts = None # preferred tts
        self.json_strings = [] # detected json string in llm output
        self.json_objects = [] # converted json objects
        self.initialize_message = None # LinguFlexMessage to raise after processing this one

    def create(self):
        created_message = LinguFlexMessage()
        created_message.tts = self.tts
        created_message.user_id = self.user_id
        return created_message
        
