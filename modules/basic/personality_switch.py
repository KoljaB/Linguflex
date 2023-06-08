import sys
sys.path.insert(0, '..')
import json
import random
import os

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage

set_section('personality_switch')

try:
    start_character = cfg[get_section()]['start_character']
except Exception as e:
    raise ValueError(configuration_parsing_error_message + ' ' + str(e))

characters =  [         
    {'name': 'Default', 
     'prompt': 'Du bist ein hilfreicher Assistent, antworte knapp.'},
    {'name': 'Witzig', 
     'prompt': 'Antworte knapp, süffisant und absurd witzig.'},
    {'name': 'Deadpool', 
     'prompt': 'Antworte knapp und im Stil von Deadpool.'},
    {'name': 'Jules Winnfield', 
     'prompt': 'Antworte knapp und im Stil von Jules Winnfield aus Pulp Fiction.'},
    {'name': 'Dude', 
     'prompt': 'Antworte knapp und im Stil des "Dude" aus "The Big Lebowski".'},
    {'name': 'Tony Stark', 
     'prompt': 'Antworte knapp und im Stil von Tony Stark aus den Marvel-Filmen.'},
    {'name': 'Jarvis', 
     'prompt': 'Antworte knapp und im Stil von Jarvis aus den Marvel-Filmen.'},
    {'name': 'Loki', 
     'prompt': 'Antworte knapp und im Stil von Loki aus den Marvel-Filmen.'},
    {'name': 'Sherlock Holmes', 
     'prompt': 'Antworte knapp und im Stil von Sherlock Holmes.'},
    {'name': 'Hannibal Lecter', 
     'prompt': 'Antworte knapp und im Stil von Dr. Hannibal Lecter.'},
    {'name': 'Captain Jack Sparrow', 
     'prompt': 'Antworte knapp und im Stil von Captain Jack Sparrow.'},
    {'name': 'Tyler Durden', 
     'prompt': 'Antworte knapp und im Stil von Tyler Durden aus Fight Club.'},
    {'name': 'John McClane', 
     'prompt': 'Antworte knapp und im Stil von John McClane aus Stirb Langsam.'},
    {'name': 'Severus Snape', 
     'prompt': 'Antworte knapp und im Stil von Severus Snape aus Harry Potter.'},
    {'name': 'Don Vito Corleone', 
     'prompt': 'Antworte knapp und im Stil von Don Vito Corleone aus "Der Pate".'},
    {'name': 'Saul Goodman', 
     'prompt': 'Antworte knapp und im Stil von Saul Goodman.'},
    {'name': 'Perry Cox', 
     'prompt': 'Antworte knapp und im Stil von Perry Cox aus Scrubs.'},
    {'name': 'Machete', 
     'prompt': 'Antworte knapp und im Stil von Machete aus dem Machete-Film.'},
    {'name': 'Yoda', 
     'prompt': 'Antworte knapp und im Stil von Yoda aus Star Wars.'},
    {'name': 'Jar Jar Binks', 
     'prompt': 'Antworte knapp und im Stil von Jar Jar Binks aus Star Wars.'},     
    {'name': 'Ferris Bueller', 
     'prompt': 'Antworte knapp und im Stil von Ferris Bueller aus Ferris macht blau.'},
    {'name': 'Frank Underwood', 
     'prompt': 'Antworte knapp und im Stil von Frank Underwood aus House of Cards.'},
    {'name': 'Terminator', 
     'prompt': 'Antworte knapp und im Stil des T-800 aus den Terminator-Filmen.'},
    {'name': 'Walter White',      
     'prompt': 'Antworte knapp und im Stil von Walter White aus Breaking Bad.'},
    {'name': 'Jesse Pinkman', 
     'prompt': 'Antworte knapp und im Stil von Jesse Pinkman aus Breaking Bad.'},
    {'name': 'Forrest Gump', 
     'prompt': 'Antworte knapp und im Stil von Forrest Gump.'},
    {'name': 'Ruby Rhod', 
     'prompt': 'Antworte knapp und im Stil von Ruby Rhod aus Das Fünfte Element.'},    
    {'name': 'Micky Maus', 
     'prompt': 'Antworte knapp und im Stil von Micky Maus.'},
    {'name': 'Emmett Brown', 
     'prompt': 'Antworte knapp und im Stil von Dr. Emmett Brown aus Zurück in die Zukunft.'},
]

character_switch_action = {
    'description': 'Charakter ändern',
    'react_to': ['charakter', 'charaktere', 'char', 'sei', 'sein', 'wirst', 'verwandel', 'verwandle', 'verwandele', 'schlüpf', 'Rolle', 'verkörpere', 'verkörper', 'identität', 'persona', 'person', 'figur', 'figuren', 'avatar', 'avatare', 'übernehm', 'übernehme', 'übernimm', 'profil', 'wechsel', 'wechsle', 'tausche', 'tauschen', 'vertausche', 'vertauschen', 'austausch', 'austauschen', 'verändere', 'ändere', 'passe', 'anpassung'],
    'example_user': 'Sei Jarvis',
    'example_assistant': 'Ok, ich bin jetzt Jarvis. {"Char":"Jarvis"}',
    'key_description': '"Char"',
    'value_description': 'Name des Charakters, zu dem gewechselt werden soll (zB Dude,Micky)',
    'keys': ['Char'],
    'instructions' : ''
}

PATH_INCOMING_CHARACTERSWITCH = 'webserver/llm_input_switch_character.txt'
PATH_INCOMING_USERDATA = 'webserver/llm_input_userdata.txt'


class PersonalitySwitchModule(JsonActionProviderModule_IF):

    def __init__(self) -> None:
        self.actions = [character_switch_action]
        self.current_character = start_character
        character_switch_action['instructions'] = f'Verfügbare Charaktere: {self.get_character_names()}'
        log(DEBUG_LEVEL_MID, f'  [character] init: {self.current_character}')
        log(DEBUG_LEVEL_MAX, f'  [character] available: {self.get_character_names()}')
        log(DEBUG_LEVEL_MAX, f'  [character] prompt: {self.get_current_prompt()}')

    def handle_input(self, 
            message: LinguFlexMessage) -> None: 
        if not message.ignore_character_prompt:
            message.character = self.current_character
            message.prompt = self.get_current_prompt() + message.prompt

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            new_character = json['Char']
            for character in characters:
                if character['name'] == new_character:
                    self.current_character = new_character
                    log(DEBUG_LEVEL_MIN, f'[character] switched to {self.current_character}')
                    break
        except json.JSONDecodeError:
            self.current_character = DEFAULT_CHAR
            log(DEBUG_LEVEL_MIN, f'[character] switch ERROR, char set to default ({DEFAULT_CHAR})')

    def cycle(self,
            message: LinguFlexMessage):
        
        if os.path.exists(PATH_INCOMING_USERDATA) and os.path.exists(PATH_INCOMING_CHARACTERSWITCH):

            with open(PATH_INCOMING_USERDATA, 'r', encoding='utf-8') as f:
                message.user_id = f.read().strip()                
            os.remove(PATH_INCOMING_USERDATA)

        
            with open(PATH_INCOMING_CHARACTERSWITCH, 'r', encoding='utf-8') as f:
                char = f.read().strip()
            os.remove(PATH_INCOMING_CHARACTERSWITCH)

            for character in characters:
                if character['name'] == char:

                    message.input = ' '
                    message.prompt = character['prompt']
                    message.clone_last_user_input = True
                    message.character = character['name']
                    message.ignore_character_prompt = True


    def get_prompt_for_character_name(self, 
            character_name: str) -> str:
        for character in characters:
            if character_name.lower() == character['name'].lower():
                return character['prompt'] + ' '
        return ''

    def get_current_prompt(self) -> None:
        return self.get_prompt_for_character_name(self.current_character) 

    def get_character_names(self) -> str:
        character_names = []
        for character in characters:
            character_names.append(character['name'])
        return ','.join(character_names)
    