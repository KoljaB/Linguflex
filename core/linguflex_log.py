import datetime
import shutil
import colorama

from colorama import Fore, Back, Style
from typing import List

colorama.init()
DEBUG_LEVEL_OFF = 0
DEBUG_LEVEL_MIN = 1
DEBUG_LEVEL_MID = 2
DEBUG_LEVEL_MAX = 3
DEBUG_LEVEL_ERR = 999
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
    first_line = True
    for line in lines:
        for i in range(0, len(line), chunk_size):
            chunk = line[i:i + chunk_size]
            if chunk.startswith(" ") and not first_line: chunk = chunk[1:]
            chunks.append(chunk)
            first_line = False        
    return chunks

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
    if len(text) > 0:
        if dbg_lvl == DEBUG_LEVEL_ERR:
            return Fore.RED + Back.WHITE + text + Style.RESET_ALL
        elif dbg_lvl >= DEBUG_LEVEL_MAX:
            return Fore.LIGHTBLACK_EX + text + Style.RESET_ALL
        elif dbg_lvl <= DEBUG_LEVEL_MIN:
            return Fore.LIGHTWHITE_EX + text + Style.RESET_ALL
    return text

def log(dbg_lvl: int, 
        text: str, 
        lf=True) -> None:
    global last_timestamp

    leading_spaces = count_leading_spaces(text) 

    if external_method is not None:
        external_method(dbg_lvl, text, lf)

    timestamp_to_print = get_elapsed_time()
    len_timestamp_to_print = len(timestamp_to_print)


    if dbg_lvl == DEBUG_LEVEL_ERR:
        timestamp_to_print = colorize(DEBUG_LEVEL_ERR, timestamp_to_print)
        colored_text = colorize(DEBUG_LEVEL_MIN, text)
        chars_left = cols - len_timestamp_to_print - 1
        fill_minus = '-' * chars_left
        print("")
        print(timestamp_to_print + '|' + Fore.WHITE + Back.RED + fill_minus + Style.RESET_ALL)
        print(timestamp_to_print + '|' + Fore.WHITE + Back.RED +  "       " +  Style.RESET_ALL)
        print(timestamp_to_print + '|' + Fore.WHITE + Back.RED +  "ERROR: " +  Style.RESET_ALL + " " + colored_text)
        print(timestamp_to_print + '|' + Fore.WHITE + Back.RED +  "       " +  Style.RESET_ALL)
        print(timestamp_to_print + '|' + Fore.RED + fill_minus + Style.RESET_ALL)
        print("")
    elif debug_level >= dbg_lvl:
        if last_timestamp == timestamp_to_print:
            timestamp_to_print = colorize(DEBUG_LEVEL_MAX, timestamp_to_print)
        else:
            last_timestamp = timestamp_to_print        
            timestamp_to_print = colorize(DEBUG_LEVEL_MID, timestamp_to_print)
            
        timestamp_to_print += '|'
        if lf:
            chars_left = cols - len_timestamp_to_print - 1
            if len(text) > chars_left or '\n' in text:
                chars_left_with_leading_spaces = chars_left - leading_spaces
                chunks = chunk_text(text, chars_left - leading_spaces)
                first_line = True
                for chunk in chunks:
                    print_line = timestamp_to_print
                    if first_line:
                        print_line += colorize(dbg_lvl, str(chunk))
                    else:
                        print_line += ' ' * leading_spaces + colorize(dbg_lvl, str(chunk))
                    if len(print_line) > 0:
                        print(print_line)
                    first_line = False
            else:
                print(timestamp_to_print + colorize(dbg_lvl, str(text)))
        else:
            print(timestamp_to_print + colorize(dbg_lvl, str(text)), end="", flush=True)


def get_timestamp() -> str:
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-5]  # behalte nur die erste Nachkommastelle

def get_elapsed_time_seconds() -> float:
    elapsed_time = datetime.datetime.now() - start_time
    return round(elapsed_time.total_seconds(), 2)