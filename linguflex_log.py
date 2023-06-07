import configparser
import datetime
import shutil
import time
import colorama

from linguflex_config import cfg
from colorama import Fore, Style
from typing import List

colorama.init()
DEBUG_LEVEL_OFF = 0
DEBUG_LEVEL_MIN = 1
DEBUG_LEVEL_MID = 2
DEBUG_LEVEL_MAX = 3
CONFIG_SECTION = 'system'
CONFIG_SECTION_NOT_FOUND_ERROR_MESSAGE = f'Configuration section for {CONFIG_SECTION} not found in config file'
CONFIG_PARSING_ERROR_MESSAGE = f'Error parsing configuration for {CONFIG_SECTION}.'
debug_level = DEBUG_LEVEL_MAX
external_method = None

def set_external_method(func) -> None:
    global external_method
    external_method = func

last_timestamp = None
start_time = datetime.datetime.now()
size = shutil.get_terminal_size()
cols = size.columns

def get_elapsed_time() -> str:
    elapsed_time = datetime.datetime.now() - start_time
    minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
    seconds = round(seconds, 1)
    minutes = str(int(minutes))
    if len(minutes) < 2: minutes = ' ' + minutes
    return f"{minutes}:{seconds:04.1f}"

def trim(text: str) -> str:
    # Remove leading spaces and line feeds
    text = text.strip()
    while text is not None and len(text) > 0 and (text[0] == " " or text[0] == "\n" or text[0] == "\r"):
        text = text[1:]        
    # # Remove trailing spaces and line feeds
    while text is not None and len(text) > 0 and (text[-1] == " " or text[-1] == "\n" or text[-1] == "\r"):
        text = text[:-1]
    return text

def chunk_text(text: str, chunk_size: int) -> List:
    chunks = []
    lines = text.split('\n')  # split text into lines
    for line in lines:
        line = trim(line)
        for i in range(0, len(line), chunk_size):
            chunk = line[i:i + chunk_size]
            chunks.append(chunk)
        chunks.append('\n')  # append a newline to preserve original line breaks
    return chunks[:-1]

# def chunk_text(text: str, 
#         chunk_size: int) -> List:
#     chunks = []
#     for i in range(0, len(text), chunk_size):
#         chunk = text[i:i + chunk_size]
#         chunks.append(chunk)
#     return chunks

def count_leading_spaces(text: str) -> int:
    count = 0
    for char in text:
        if char == " ":
            count += 1
        else:
            break
    return count

def colorize(dbg_lvl: int,
        text: str) -> str:
    text = trim(text)
    if len(text) > 0:
        if dbg_lvl >= DEBUG_LEVEL_MAX:
            return Fore.LIGHTBLACK_EX + text + Style.RESET_ALL
        elif dbg_lvl <= DEBUG_LEVEL_MIN:
            return Fore.LIGHTWHITE_EX + text + Style.RESET_ALL
    return text

def log(dbg_lvl: int, 
        text: str, 
        lf=True) -> None:
    global last_timestamp
    if external_method is not None:
        external_method(dbg_lvl, text, lf)
    if debug_level >= dbg_lvl:
        current_timestamp = get_elapsed_time()
        if last_timestamp == current_timestamp:
            timestamp_to_print = colorize(DEBUG_LEVEL_MAX, current_timestamp)
        else:
            timestamp_to_print = colorize(DEBUG_LEVEL_MID, get_elapsed_time())
            last_timestamp = current_timestamp        
        timestamp_to_print += '|'
        if lf:
            chars_left = cols - len(timestamp_to_print) - 1
            if len(text) > chars_left:
                leading_spaces = count_leading_spaces(text) 
                chunks = chunk_text(text, chars_left - leading_spaces)
                first_line = True
                for chunk in chunks:
                    print_line = timestamp_to_print
                    chunk = trim(chunk)
                    if first_line:
                        print_line += colorize(dbg_lvl, str(chunk))
                    else:
                        print_line += ' ' * leading_spaces + colorize(dbg_lvl, str(chunk))
                    if len(print_line) > 0: print(print_line)
                    first_line = False
            else:
                print(timestamp_to_print + colorize(dbg_lvl, str(text)))
        else:
            print(timestamp_to_print + colorize(dbg_lvl, str(text)), end="", flush=True)

if not cfg.has_section(CONFIG_SECTION):
    raise ValueError(CONFIG_SECTION_NOT_FOUND_ERROR_MESSAGE)
try:
    debug_level = cfg['system'].getint('debuglevel', 2)
except Exception as e:
    raise ValueError(CONFIG_PARSING_ERROR_MESSAGE + ' ' + str(e))

def get_timestamp() -> str:
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-5]  # behalte nur die erste Nachkommastelle

def get_elapsed_time_seconds() -> float:
    elapsed_time = datetime.datetime.now() - start_time
    return round(elapsed_time.total_seconds(), 2)
