import sys
sys.path.insert(0, '..')

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from depot_summary_helper import ComdirectInformationParser
from datetime import datetime

set_section('depot_summary')

try:
    summary_url = cfg[get_section()].get('summary_url')
    depot_urls = cfg[get_section()].get('depot_urls').split(',')
    depot_names = cfg[get_section()].get('depot_names').split(',')
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))  

portfolio_action = {
    'description': '',
    'react_to': ['aktie','depot','stocks','etfs','börse','märkten','markt','invest'],
    'example_user': '',
    'example_assistant': '',
    'key_description': '',
    'value_description': '',
    'keys': ['Aktien'],
    'instructions' : 'Wenn du zu den Aktien, zum Depot oder den Investments des Benutzers gefragt wirst, schreibe lediglich das JSON {"Aktien": "Anfrage"}, sonst nichts.'
}

portfolio_summarization_input = "Fasse die heutige Entwicklung des Depots zusammen. " 

portfolio_summarization_prompt = """
Fasse die wichtigsten Informationen zur heutigen Entwicklung des Depots zusammen. \
Runde große Beträge auf Werte auf hunderter oder tausender auf oder ab. \
Lass Einleitungen und Hinweise weg, gib nur eine knappes Fazit.

Hier die Infos zum Depot:
""" 

class DepotSummary(JsonActionProviderModule_IF):

    def __init__(self) -> None:
        self.actions = [portfolio_action]

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'Aktien' in json.keys() and json['Aktien'] == 'Anfrage':

                log(DEBUG_LEVEL_MID, f'  [depot] fetching data for summary link')
                info_gesamt = ComdirectInformationParser(summary_url).get_summarization(False)

                info_depots = {}
                for i, url in enumerate(depot_urls):
                    depot_name = depot_names[i] if i < len(depot_names) else "Unnamed Depot"
                    log(DEBUG_LEVEL_MID, f'  [depot] fetching portfolio data {i+1}/{len(depot_urls)}')
                    info_depots[depot_name] = ComdirectInformationParser(url).get_summarization()

                summarization = "Überblick:\n" + info_gesamt + "\n"
                for depot_name, info in info_depots.items():
                    summarization += f"{depot_name}, Details:\n{info}\n"

                log(DEBUG_LEVEL_MID, f'  [depot] creating summary of raw data: ')
                log(DEBUG_LEVEL_MID, f'  [depot] ' + summarization)

                # raise new message since we want to call the llm again
                create_new_response = message.create()                
                create_new_response.input = portfolio_summarization_input + message.input
                create_new_response.prompt = portfolio_summarization_prompt + summarization
                create_new_response.raise_actions = 'depot_summary'
                create_new_response.no_input_processing = True
                create_new_response.skip_input = True
                create_new_response.remove_from_history = True
                message.skip_output = True
                message.initialize_message = create_new_response
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [depot] ERROR:' + str(e))