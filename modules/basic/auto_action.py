import sys
sys.path.insert(0, '..')
import os
from datetime import datetime

from linguflex_interfaces import Module_IF, JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage

FAIL_DETECTION_STRINGS = [
    'sorry', 
    'tut mir leid',
    'keine ahnung', 
    'keinen zugriff',
    'keine informationen', 
    'kann ich ihnen keine', 
    'kann ich nicht sagen', 
    'kann ich keine', 
    'nicht beantworten',
    'keine vorhersage',
    'keine vorhersagefähigkeit',
    'keine vorhersagefähigkeiten',
    'unmöglich vorherzusagen',
    'keine echtzeitinformationen',
    'keine aktuellen informationen',
    'ich keine möglichkeit', 
    'diese Frage nicht',
    ]

fail_detect_prompt = '''\
Folgende Konversation bestehend aus Anfrage und Antwort:
Anfrage: ```{}```
Antwort: ```{}```
Konnte die Frage beantwortet bzw die Anfrage erfüllt werden? Antworte ausschließlich mit JA oder NEIN.
'''

autoaction_prompt = '''\
Du bist Experte in der Anwendung von Fähigkeiten und Aktionen zur Erfüllung von Anfragen. \

Folgende Fähigkeiten und Aktionen kannst du nun anwenden: \
{}

Die zu erfüllende Anfrage: \
```{}```

Jetzt wollen wir dies Schritt für Schritt prüfen, ob welche der Fähigkeiten und Aktionen zur Erfüllung der Anfragen hilfreich sein könnte. \
Gehe die dir zu Verfügung gestellten Fähigkeiten und Aktionen der Reihe nach durch. \
Finde die Aktion, deren Ergebnis die Anfrage bestmöglich erfüllt oder zu deren Erfüllung bestmöglich beitragen kann, \
nutze beispielsweise \"Echtzeit-Informationen aus dem Internet abrufen\" nutzen, wenn es wenn es um aktuelle Anfragen geht \
oder um Anfragen, die aus deiner Sicht in der Zukunft stattfinden. \
Falls du eine solche Aktion gefunden hast, gib das zugehörige JSON ohne jeden weiteren Kommentar aus; andernfalls gib eine bestmögliche Antwort auf die Anfrage.
'''

empty_action = {
    'description': '',
    'react_to': [],
    'example_user': '',
    'example_assistant': '{"":""}',
    'key_description': '',
    'value_description': '',
    'keys': [],
    'instructions' : ''
}

class JV_AutoAction(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [empty_action]
        pass

    def handle_input(self, 
            message: LinguFlexMessage) -> None: 
        cur_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cur_date = datetime.now().strftime("%d.%m.%Y")
        cur_time = datetime.now().strftime("%H:%M")
        time_string = f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr.'


    def detect_failed_answer(self,
            answer: str) -> bool:
        answer_lower = answer.lower()
        for fail_string in FAIL_DETECTION_STRINGS:
            if fail_string in answer_lower:
                return True
        return False

    def output_reaction(self, 
            message: LinguFlexMessage) -> None: 
        
        if 'auto_action' in message.ignore_actions:
            return
        
        if self.detect_failed_answer(message.output) and not message.skip_input:           
            # we may have a possible fail answer, let's verify if answer failed by asking the llm
            log(DEBUG_LEVEL_MAX, f'  [autoaction] checking possible failed answer')

            create_new_response = message.create()
            create_new_response.input = fail_detect_prompt.format(message.input, message.output)
            create_new_response.no_history = True
            create_new_response.original_input = message.input
            create_new_response.original_output = message.output
            create_new_response.original_output_user = message.output_user
            create_new_response.no_input_processing = True
            create_new_response.raise_actions = 'auto_action'
            create_new_response.skip_input = True
            create_new_response.llm = 'gpt-3.5-turbo'
            create_new_response.remove_from_history = True       

            message.skip_output = True
            message.initialize_message = create_new_response               

        if message.raise_actions == 'auto_action':
            if 'NEIN' in message.output:
                log(DEBUG_LEVEL_MID, f'  [autoaction] failed answer confirmed, choosing action')

                # answer failed confirmed, now we ask the llm to choose an action
                create_new_response = message.create()
                create_new_response.input = autoaction_prompt.format(self.server.get_full_action_string(message), message.original_input)
                create_new_response.no_history = True
                create_new_response.original_input = message.original_input
                create_new_response.original_output = message.output
                create_new_response.original_output_user = message.output_user
                create_new_response.no_input_processing = True
                create_new_response.skip_input = True
                create_new_response.remove_from_history = True       

                message.skip_output = True
                message.initialize_message = create_new_response               
            else:
                log(DEBUG_LEVEL_MID, f'  [autoaction] no FAIL answer')
                message.output = message.original_output
                message.output_user = message.original_output_user