from core import ActionModule, Request, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function
from pydantic import Field
from datetime import datetime, timedelta

auto_action_function = 'hard_to_answer'

@linguflex_function
def hard_to_answer():
    "Call whenever providing a 100% satisfactory response to the request is not easy"
    return None

prompt = """"You are an expert in calling functions to answer difficult requests. \
Read, analyze and understand all available functions. \
Think deep carefully and step-by-step about which function call would likely contribute most to generating the best possible answer to the request. \
"""

class AllActionProvider(ActionModule):        
    def on_function_executed(self, request: Request, name: str, type: str, arguments) -> None: 
        
        if name == auto_action_function:
            full_actions_request = request.new()
            full_actions_request.prompt = prompt
            full_actions_request.exclude_actions = name
            full_actions_request.include_all_actions = True