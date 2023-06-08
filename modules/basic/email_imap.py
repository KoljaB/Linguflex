import sys
sys.path.insert(0, '..')

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from email_imap_helper import EmailFetcher
from datetime import datetime

set_section('email_imap')

try:
    server = cfg[get_section()]['server']
    username = cfg[get_section()]['username']
    password = cfg[get_section()]['password']
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))


emails_action = {
    'description': 'E-Mails abrufen',
    'react_to': ['mail','mails','email','emails','e-mail','e-mails'],
    'example_user': 'Wie sind meine E-Mails?',
    'example_assistant': '{"EMail": "Datenabruf"}',
    'key_description': 'EMail',
    'value_description': 'Datenabruf',
    'keys': ['EMail'],
    'instructions' : 'Gib wenn du zu E-Mails befragt wirst das JSON {"EMail": "Datenabruf"} aus, sonst nichts.'
}

class EMailModule(JsonActionProviderModule_IF):

    def __init__(self) -> None:
        self.actions = [emails_action]
        self.fetcher = EmailFetcher(server, username, password)

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'EMail' in json.keys() and json['EMail'] == 'Datenabruf':
                log(DEBUG_LEVEL_MID, f'  [mail] checking mails')

                # fetch mails
                emails = self.fetcher.get_mails(5)
                emails.reverse()
                log(DEBUG_LEVEL_MAX, f'  [mail] mails fetched: ' + str(len(emails)))

                # create summary for llm
                summary = ''
                for email in emails:
                    email['content'] = self.fetcher.remove_links(email['content'])
                    summary += self.fetcher.summarize(email) + "\n"
                summary = (summary[:5000] + '..') if len(summary) > 5000 else summary                    

                # raise new message since we want to call the llm again
                create_new_response = message.create()                
                create_new_response.input = "Gib mir eine Zusammenfassung relevanter, wichtiger EMails."
                cur_date = datetime.now().strftime("%d.%m.%Y")
                cur_time = datetime.now().strftime("%H:%M")
                time_string = f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr. '                
                create_new_response.prompt = time_string + f"Meine EMails: ´´´{summary}´´´"
                create_new_response.skip_input = True
                create_new_response.remove_from_history = True
                message.skip_output = True
                message.initialize_message = create_new_response
            

        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [mail] ERROR:' + str(e))