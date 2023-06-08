import sys
sys.path.insert(0, '..')
import os
from datetime import datetime

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from google_information_helper import GoogleSearchAPI

set_section('google_information')

API_KEY_NOT_FOUND_ERROR_MESSAGE = 'Serp API-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_SERP_API_KEY.'

FAIL_DETECTION_STRINGS = [
    'keine informationen', 
    'kann ich ihnen keine', 
    'kann ich keine', 
    'keine echtzeitinformationen',
    'keine aktuellen informationen'
    ]

# Import Serp API-Key from either registry (LINGU_SERP_API_KEY) or config file jv_google/serp_api_key
api_key = os.environ.get('LINGU_SERP_API_KEY')
if api_key is None:
    try:
        api_key = cfg[get_section()]['serp_api_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if api_key is None:
    raise ValueError(API_KEY_NOT_FOUND_ERROR_MESSAGE)

google_action = {
    'description': 'Echtzeit-Informationen aus dem Internet abrufen',
    'react_to': ['google', 'googlen', 'googeln', 'ergoogeln', 'ergooglen', 'googel', 'suche', 'such', 'internet', 'web', 'netz', 'browse', 'suchmaschine', 'online', 'recherche', 'information', 'ergebnis', 'suchanfrage', 'suchfeld', 'suchbegriff', 'suchergebnis', 'surf', 'websites', 'world wide web', 'www', 'webseite', 'suchen', 'onlinesuche', 'websuche', 'internetrecherche', 'find', 'finde', 'herausfinden'],
    'example_user': 'Wer war 2023 Meister?',
    'example_assistant': '{"Google":"Deutscher Meister 2023"}',
    'key_description': '"Google"',
    'value_description': 'Geeignete Stichwort(e) zur Erzielung optimaler Google-Suchergebnisse zur Beantwortung der Anfrage',
    'keys': ['Google'],
    'instructions' : ''
}

class GoogleInformationModule(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [google_action]
        self.google = GoogleSearchAPI(api_key)

    def handle_input(self, 
            message: LinguFlexMessage) -> None: 
        cur_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur_date = datetime.now().strftime("%d.%m.%Y")
        cur_time = datetime.now().strftime("%H:%M")
        time_string = f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr.'

        google_action['instructions'] = 'Schreibe nur das JSON, sonst nichts. ' + time_string + ' Beispiel User: \'Google, wie Borussia Dortmund heute gespielt hat.\'. Assistant: \'{"Google":"' + cur_date + ' Ergebnis Borussia Dortmund"}\' '

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            search_terms = json['Google']

            log(DEBUG_LEVEL_MID, f'  [google] searching for: {search_terms}')
            google_answer = self.google.search(json['Google'])
            log(DEBUG_LEVEL_MAX, f'  [google] answer: {google_answer}')

            create_new_response = message.create()
            create_new_response.input = message.original_input
            create_new_response.skip_input = True
            cur_date = datetime.now().strftime("%d.%m.%Y")
            cur_time = datetime.now().strftime("%H:%M")
            time_string = f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr.'
            create_new_response.prompt_end = f'Nutze folgenden Kontext zur bestmöglichen Beantwortung der Anfrage: ´´´{google_answer} {time_string}´´´\n'
            create_new_response.ignore_actions = 'google_information, auto_action'
            create_new_response.no_input_processing = True            
            create_new_response.remove_from_history = True
            create_new_response.no_history = True

            message.skip_output = True
            message.initialize_message = create_new_response
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [google] ERROR:' + e)

    def detect_failed_answer(self,
            answer: str) -> bool:
        answer_lower = answer.lower()
        for fail_string in FAIL_DETECTION_STRINGS:
            if fail_string in answer_lower:
                return True
        return False