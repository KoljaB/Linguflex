import json

from .linguflex_request import Request
from .linguflex_log import (
    log,
    DEBUG_LEVEL_OFF,
    DEBUG_LEVEL_MIN,
    DEBUG_LEVEL_MID,
    DEBUG_LEVEL_MAX,
)

def trim(text: str) -> str:
    # Remove leading spaces and line feeds
    text = text.strip()
    while text is not None and len(text) > 0 and (text[0] == " " or text[0] == "\n" or text[0] == "\r"):
        text = text[1:]        
    # # Remove trailing spaces and line feeds
    while text is not None and len(text) > 0 and (text[-1] == " " or text[-1] == "\n" or text[-1] == "\r"):
        text = text[:-1]
    return text

def name_in_json(json_obj, 
        names: str, 
        search_only_keys = False) -> bool:
    def find_name(obj): 
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    if find_name(value):
                        return True
                elif search_only_keys == False and isinstance(value, str) and value in names:
                    return True
                elif isinstance(value, str) and key in names:
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    if find_name(item):
                        return True
                elif isinstance(item, str) and item in names:
                    return True
        return False
    return find_name(json_obj)    


def extract_json(request: Request) -> None:
    
    stack = []
    request.json_strings = []
    request.json_objects = []
    request.output_user = request.output

    for i, char in enumerate(request.output_user):
        if char == '{':
            stack.append(i)
        elif char == '}':
            start = stack.pop()
            if not stack:
                json_str = request.output_user[start:i+1]
                try:
                    json_obj = json.loads(json_str)
                except json.JSONDecodeError:
                    try:
                        json_str = json_str.replace("'", '"')
                        json_obj = json.loads(json_str)
                    except json.JSONDecodeError:
                        log(DEBUG_LEVEL_MIN, f'JSON Error decoding string "{json_str}"')
                        continue
                request.json_objects.append(json_obj)
                request.json_strings.append(json_str)
                request.output_user = request.output_user[:start] + request.output_user[i+1:]

    request.output_user = trim(request.output_user)