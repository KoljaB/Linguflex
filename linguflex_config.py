import configparser
import sys

CONFIG_FILE_PATH = 'config.txt'
config_file_path = CONFIG_FILE_PATH
if len(sys.argv) >= 2:
    config_file_path = sys.argv[1]
configuration_section_not_found_error_message = 'Configuration section not found in config file'
configuration_parsing_error_message = 'Error parsing configuration'
configuration_section_name = None

def set_section(section_name: str) -> None:
    global configuration_section_name, configuration_section_not_found_error_message, configuration_parsing_error_message
    configuration_section_name = section_name
    configuration_section_not_found_error_message = f'Configuration section for {configuration_section_name} not found in config file'
    configuration_parsing_error_message = f'Error parsing configuration for {configuration_section_name}.'
    if not cfg.has_section(configuration_section_name):
        raise ValueError(configuration_section_not_found_error_message)

def get_section() -> str:
    return configuration_section_name

cfg = configparser.ConfigParser(allow_no_value=True)
cfg.read(config_file_path)