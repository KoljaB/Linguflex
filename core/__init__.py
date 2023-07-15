# __init__.py
from .linguflex_log import (
    log,
    DEBUG_LEVEL_OFF,
    DEBUG_LEVEL_MIN,
    DEBUG_LEVEL_MID,
    DEBUG_LEVEL_MAX,
    DEBUG_LEVEL_ERR,
    debug_level,
    set_external_method,
    get_elapsed_time,
)
from .linguflex_config import cfg, parser, items, Config
from .linguflex_request import Request
from .linguflex_functions import linguflex_function, LinguFlexBase, tokens_function, max_tokens_answer, max_tokens_result

from .linguflex_interfaces import (
    BaseModule, 
    InputModule, 
    SpeechRecognitionModule, 
    TextToSpeechModule, 
    TextGeneratorModule, 
    ActionModule
)
from .linguflex_texthelper import trim, name_in_json, extract_json
from .linguflex_server import LinguFlexServer
from .linguflex_sound import play_sound, shutdown_sound