import sys
sys.path.insert(0, '..')

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from news_summary_helper import NewsParser
from datetime import datetime

news_action = {
    'description': 'Nachrichten abrufen',
    'react_to': ['neues','nachricht','news','update','aktuell','bericht','ereignis','information','heutig','geschehnis','schlagzeilen','geschehen','themen','tagesschau','ist los','so los'],
    'example_user': 'Was gibt es neues?',
    'example_assistant': '{"News": "Hauptnachrichten"}',
    'key_description': 'News',
    'value_description': '"Hauptnachrichten", "Wirtschaft", "Technik", "Forschung", "Inland", "Ausland" oder "Gesellschaft"',
    'keys': ['News'],
    'instructions' : 'Falls du Nachrichten abrufen willst gib nur das JSON dazu aus, zB {"News": "Hauptnachrichten"} oder {"News": "Technik"}, sonst nichts. Wenn der Benutzer kein konkretes Themengebiet angegeben hat, gib {"News": "Hauptnachrichten"} aus.'
}

news_summarization_input = "Fasse die heutigen Nachrichten zusammen. " 

news_summarization_prompt = """
Fasse die wichtigsten Informationen zu den heutigen Nachrichten zusammen. \
Lass Einleitungen und Hinweise weg, gib nur eine knappes Fazit.

Hier die Nachrichten:
""" 

class NewsModule(JsonActionProviderModule_IF):

    def __init__(self) -> None:
        self.actions = [news_action]

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'News' in json.keys() and json['News'] in news_action['value_description']:

                log(DEBUG_LEVEL_MID, f'  [news] fetching data')

                if json['News'] == 'Hauptnachrichten':
                    news = NewsParser().get_main_summarization()
                elif json['News'] == 'Technik':
                    news = NewsParser().get_technik_summarization()
                elif json['News'] == 'Wirtschaft':
                    news = NewsParser().get_economy_summarization()
                elif json['News'] == 'Forschung':
                    news = NewsParser().get_forschung_summarization()
                elif json['News'] == 'Inland':
                    news = NewsParser().get_inland_summarization()
                elif json['News'] == 'Ausland':
                    news = NewsParser().get_ausland_summarization()
                elif json['News'] == 'Gesellschaft':
                    news = NewsParser().get_gesellschaft_summarization()

                log(DEBUG_LEVEL_MID, f'  [news] creating summary of raw data: ')
                log(DEBUG_LEVEL_MID, f'  [news] ' + news)

                # raise new message since we want to call the llm again
                create_new_response = message.create()                
                create_new_response.input = news_summarization_input + message.input
                create_new_response.prompt = news_summarization_prompt + news
                create_new_response.raise_actions = 'news_summary'
                create_new_response.skip_input = True
                create_new_response.remove_from_history = True
                message.skip_output = True
                message.initialize_message = create_new_response
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [news] ERROR:' + str(e))