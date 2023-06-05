import sys
sys.path.insert(0, '../..')

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from google_calendar_helper import GoogleCalendarAPI  
from datetime import datetime, timedelta

calendar_retrieve_action = {
    'description': 'Kalenderdaten abrufen',
    'react_to': ['kalender', 'termin', 'steht an', 'zu tun', 'plan', 'verabred', 'ereignis', 'treffen', 'zeitplan', 'tagesordnung', 'besprechung', 'veranstaltung', 'datum', 'tag', 'woche', 'monat', 'jahr', 'demnächst', 'beschäftigt', 'freizeit', 'verfügbar', 'belegt', 'ausgebucht', 'verschieben', 'stornieren', 'bestätigen', 'erinnerung', 'alarm', 'fällig', 'deadline', 'frist', 'zeitfenster'],
    'example_user': 'Was sind meine nächsten Termine?',
    'example_assistant': '{"KalenderLesen": "Termine"}',
    'key_description': 'KalenderLesen',
    'value_description': 'Termine',
    'keys': ['KalenderLesen'],
    'instructions' : ''
}

calendar_addevent_action = {
    'description': 'Ereignis in den Kalender eintragen',
    'react_to': ['trag', 'merke', 'kalender', 'termin', 'ereignis', 'treffen', 'veranstaltung', 'erinner'],
    'example_user': 'Erinnere mich morgen um 16 Uhr an die schwarze Mülltonne',
    'example_assistant': '{"KalenderSchreiben": "Schwarze Mülltonne", "Start": "2023-06-01T16:00:00+00:00"}',
    'key_description': '"KalenderSchreiben", "Start" und optional "Ende"',
    'value_description': 'Zeitangaben IMMER (!) in ISO 8601 wie im Beispiel',
    'keys': ['KalenderSchreiben', 'Start', 'Ende'],
    'instructions' : ''
}

calendar_summarization_input = "Gib mir einen Überblick über meine nächsten Termine. " 

calendar_summarization_prompt = """
Gib mir einen Überblick über meine innerhalb der nächsten Woche anstehenden Termine. 

Hier die Infos zu den Terminen:
""" 

class JV_Calendar(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [calendar_retrieve_action, calendar_addevent_action]


    def on_keywords_in_input(self, 
            message: LinguFlexMessage,
            keywords_in_input: str) -> None: 
        
        cur_date = datetime.now().strftime("%d.%m.%Y")
        cur_time = datetime.now().strftime("%H:%M")
        time_string = f'Das heutige Datum ist {cur_date}, es ist {cur_time} Uhr. '
                         
        calendar_addevent_action['instructions'] = time_string


    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'KalenderLesen' in json.keys() and json['KalenderLesen'] == 'Termine':

                log(DEBUG_LEVEL_MID, f'  [calendar] fetching data')

                api = GoogleCalendarAPI()
                api.authenticate()
                events = api.get_upcoming_events(10)
                
                termine = ''
                if not events:
                    termine = 'Keine kommenden Termine gefunden.'
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    termine += str(start) + ' ' + str(event['summary']) + '\n'

                log(DEBUG_LEVEL_MID, f'  [calendar] creating summary of raw data: ')
                log(DEBUG_LEVEL_MID, f'  [calendar] ' + termine)

                cur_date = datetime.now().strftime("%d.%m.%Y")
                time_string = f'Das heutige Datum ist {cur_date}. '

                create_new_response = message.create()                
                create_new_response.input = calendar_summarization_input + message.input
                create_new_response.prompt = time_string + calendar_summarization_prompt + termine
                create_new_response.raise_actions = 'jv_calendar'
                create_new_response.skip_input = True
                create_new_response.remove_from_history = True
                message.skip_output = True
                message.initialize_message = create_new_response

            if 'KalenderSchreiben' in json.keys() and 'Start' in json.keys():

                log(DEBUG_LEVEL_MID, f'  [calendar] preparing entry')

                text = json['KalenderSchreiben']
                start = json['Start']
                start_datetime = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                end_datetime = start_datetime + timedelta(minutes=30)

                api = GoogleCalendarAPI()
                api.authenticate()
                log(DEBUG_LEVEL_MID, f'  [calendar] writing into calendar, text: {text}, start: ' + str(start_datetime) + ', end: ' + str(end_datetime))
                api.create_event(text, start_datetime, end_datetime)

        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [calendar] ERROR:' + str(e))