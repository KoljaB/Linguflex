from colorama import Fore, Back, Style
from threading import Lock
from typing import List
from enum import Enum
import colorama
import datetime
import shutil
import os

colorama.init()


class Level(Enum):
    """
    Enum for different levels of debugging and logging.
    Includes Off, Low, Dbg, Info, High, Warn, and ERR levels.
    """
    Off = -1
    Low = 0
    Dbg = 1
    Info = 2
    High = 3
    Warn = 998
    ERR = 999


CONFIG_SECTION = 'system'
CONFIG_SECTION_NOT_FOUND_ERROR_MESSAGE = \
    f"Configuration section for {CONFIG_SECTION} not found in config file"
CONFIG_PARSING_ERROR_MESSAGE = \
    f"Error parsing configuration for {CONFIG_SECTION}."

LOG_DIR = "logs"
# Create the log directory if it does not exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
LOG_FILE_TIME = datetime.datetime.now().strftime("%H-%M-%S")
LOG_FILE_DATETIME = f"{LOG_FILE_DATE}_{LOG_FILE_TIME}"
LOG_FILE_NAME = f"logfile_{LOG_FILE_DATETIME}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

# Delete the log file if it exists
if os.path.exists(LOG_FILE_PATH):
    os.remove(LOG_FILE_PATH)

debug_level = Level.Low
last_timestamp = None
start_time = datetime.datetime.now()
size = shutil.get_terminal_size()
cols = size.columns
log_lock = Lock()
external_method = None


def set_external_method(func) -> None:
    """
    Assigns an external method to be used for logging.

    Args:
        func (callable): A function to be used for external logging.
    """
    global external_method
    external_method = func


def get_elapsed_time() -> str:
    """
    Calculates the elapsed time since the script started.

    Returns:
        str: Elapsed time in the format 'MM:SS.s'.
    """
    elapsed_time = datetime.datetime.now() - start_time
    minutes, seconds = divmod(elapsed_time.total_seconds(), 60)
    seconds = round(seconds, 1)
    minutes = str(int(minutes))
    if len(minutes) < 2:
        minutes = ' ' + minutes
    return f"{minutes}:{seconds:04.1f}"


def trim(text: str) -> str:
    """
    Trims leading and trailing spaces and line feeds from a string.

    Args:
        text (str): The text to be trimmed.

    Returns:
        str: The trimmed text.
    """
    # Remove leading spaces and line feeds
    text = text.strip()
    while text is not None \
            and len(text) > 0 \
            and (text[0] == " " or text[0] == "\n" or text[0] == "\r"):

        text = text[1:]
    # # Remove trailing spaces and line feeds
    while text is not None \
            and len(text) > 0 \
            and (text[-1] == " " or text[-1] == "\n" or text[-1] == "\r"):

        text = text[:-1]
    return text


def chunk_text(text: str, chunk_size: int) -> List:
    """
    Splits text into chunks of a specified size.

    Args:
        text (str): Text to be chunked.
        chunk_size (int): Size of each chunk.

    Returns:
        List[str]: List of text chunks.
    """
    chunks = []
    lines = text.split('\n')  # split text into lines
    first_line = True
    for line in lines:
        for i in range(0, len(line), chunk_size):
            chunk = line[i:i + chunk_size]
            if chunk.startswith(" ") and not first_line:
                chunk = chunk[1:]
            chunks.append(chunk)
            first_line = False
    return chunks


def count_leading_spaces(text: str) -> int:
    """
    Counts the number of leading spaces in a string.

    Args:
        text (str): Text to check for leading spaces.

    Returns:
        int: Number of leading spaces.
    """
    count = 0
    for char in text:
        if char == " ":
            count += 1
        else:
            break
    return count


def colorize(dbg_lvl: Level,
             text: str
             ) -> str:
    """
    Applies color formatting to the text based on the debug level.

    Args:
        dbg_lvl (Level): The debugging level.
        text (str): Text to be colorized.

    Returns:
        str: Colorized text.
    """
    if len(text) > 0:
        if dbg_lvl == Level.ERR:
            return Fore.RED + Back.WHITE + text + Style.RESET_ALL
        elif dbg_lvl.value <= Level.Dbg.value:
            return Fore.LIGHTBLACK_EX + text + Style.RESET_ALL
        elif dbg_lvl.value >= Level.High.value:
            return Fore.LIGHTWHITE_EX + text + Style.RESET_ALL
    return text


def _log(dbg_lvl: Level,
         text: str,
         lf=True,
         flush=False
         ) -> None:
    """
    Internal logging function with timestamp, level, and color formatting.

    Args:
        dbg_lvl (Level): The debugging level.
        text (str): Text to log.
        lf (bool): If True, add line feed after the log. Default is True.
        flush (bool): If True, flush the output immediately. Default is False.
    """
    global last_timestamp

    with log_lock:

        if isinstance(dbg_lvl, int):
            raise ValueError("Received an integer as 'dbg_lvl' parameter of "
                             "the log method, but must be of type 'Level'.")

        leading_spaces = count_leading_spaces(text)

        if external_method is not None:
            external_method(dbg_lvl, text, lf)

        timestamp_to_print = get_elapsed_time()
        len_timestamp_to_print = len(timestamp_to_print)

        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:

            if dbg_lvl == Level.ERR:
                # play_sound("error")
                timestamp_to_print = colorize(Level.ERR, timestamp_to_print)
                chars_left = cols - len_timestamp_to_print - 1
                fill_minus = '-' * chars_left
                print("")
                print(timestamp_to_print + '|' + Fore.WHITE + Back.RED
                    + fill_minus + Style.RESET_ALL)
                print(timestamp_to_print + '|' + Fore.WHITE + Back.RED
                    + "       " + Style.RESET_ALL)
                
                lines = text.split('\n')
                for line in lines:
                    colored_text = colorize(Level.Low, line)
                    print(timestamp_to_print + '|' + Fore.WHITE + Back.RED
                        + "ERROR: " + Style.RESET_ALL + " " + colored_text)
                print(timestamp_to_print + '|' + Fore.WHITE + Back.RED
                    + "       " + Style.RESET_ALL)
                print(timestamp_to_print + '|' + Fore.RED + fill_minus
                    + Style.RESET_ALL)
                print("")

                # Log to file without colorization
                log_file.write(f"\n{timestamp_to_print}|ERROR: {text}\n\n")

            elif debug_level.value <= dbg_lvl.value:
                if last_timestamp == timestamp_to_print:
                    timestamp_to_print = colorize(Level.Dbg, timestamp_to_print)
                else:
                    last_timestamp = timestamp_to_print
                    timestamp_to_print = colorize(Level.Info, timestamp_to_print)

                timestamp_to_print += '|'
                last_timestamp_to_print = last_timestamp + '|'
                if lf:
                    chars_left = cols - len_timestamp_to_print - 1
                    if len(text) > chars_left or '\n' in text:
                        chunks = chunk_text(text, chars_left - leading_spaces)
                        first_line = True
                        for chunk in chunks:
                            print_line_uncolorized = last_timestamp_to_print
                            print_line = timestamp_to_print
                            if first_line:
                                print_line_uncolorized += chunk
                                print_line += colorize(dbg_lvl, str(chunk))
                            else:
                                print_line_uncolorized += ' ' * leading_spaces
                                print_line_uncolorized += chunk
                                print_line += ' ' * leading_spaces
                                print_line += colorize(dbg_lvl, str(chunk))

                            if len(print_line) > 0:
                                if flush:
                                    print(print_line, end="", flush=True)
                                    log_file.write(print_line_uncolorized)
                                else:
                                    print(print_line)
                                    log_file.write(print_line_uncolorized + "\n")
                            first_line = False
                    else:
                        if flush:
                            print(
                                timestamp_to_print +
                                colorize(dbg_lvl, str(text)),
                                end="", flush=True)
                            log_file.write(
                                last_timestamp_to_print + str(text))
                        else:
                            print(
                                timestamp_to_print +
                                colorize(dbg_lvl, str(text))
                                )
                            log_file.write(
                                last_timestamp_to_print + str(text) + "\n")
                else:
                    print(
                        timestamp_to_print + colorize(dbg_lvl, str(text)),
                        end="", flush=True)
                    log_file.write(
                        last_timestamp_to_print + str(text))


def get_timestamp() -> str:
    """
    Retrieves the current time in a specific format.

    Returns:
        str: The current timestamp.
    """
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-5]


def get_elapsed_time_seconds() -> float:
    """
    Calculates the elapsed time in seconds since the script started.

    Returns:
        float: Elapsed time in seconds.
    """
    elapsed_time = datetime.datetime.now() - start_time
    return round(elapsed_time.total_seconds(), 2)


class LinguLog():
    """
    Class for logging at different levels including
      warn, info, debug, high, error, and low.
    Methods are wrappers around the _log function with specific levels.
    Args for methods:
        text (str): Debug message to log.
        lf (bool): If True, add line feed after logging. Default is True.
        flush (bool): If True, flush the output immediately. Default is False.
    """
    def wrn(self,
            text: str,
            lf=True,
            flush=False
            ) -> None:
        _log(Level.Warn, text, lf, flush)

    def inf(self,
            text: str,
            lf=True,
            flush=False
            ) -> None:
        _log(Level.Info, text, lf, flush)

    def dbg(self,
            text: str,
            lf=True,
            flush=False
            ) -> None:
        _log(Level.Dbg, text, lf, flush)

    def hgh(self,
            text: str,
            lf=True,
            flush=False
            ) -> None:
        _log(Level.High, text, lf, flush)

    def err(self,
            text: str,
            lf=True,
            flush=False
            ) -> None:
        _log(Level.ERR, text, lf, flush)

    def low(self,
            text: str,
            lf=True,
            flush=False
            ) -> None:
        _log(Level.Low, text, lf, flush)


log = LinguLog()
