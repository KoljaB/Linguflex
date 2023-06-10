import sys
sys.path.insert(0, '..')
import json
import random

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage


emoji_game_prompt = '''\
Lass uns ein Spiel spielen. Du bist ein Emoji-Künstler und Experte für Popkultur. Wähle selbständig einen zufälligen Film, ein Buch oder eine Serie aus.

Beschreibe das ausgewählte Werk lediglich mit Emojis möglichst prägnant und achte dabei folgende Instruktionen:
- meide 🎬, 📖 oder 📺; diese Emojis sind in meiner Kultur beleidigend
- verwende kein Emoji mehrfach
- ein gutes Emoji visualisiert ein wesentliches Merkmal des Werks, zB eine Hauptfigur, einen zentralen Gegenstand oder einen Haupthandlungsort
- verwendete Emojis werden in derselben Reihenfolge ausgegeben, in der sie thematisch auch im Werk vorkommen

Du wirst immer einen zufälliges Werk auswählen. Gib nun deine Antwort ohne dabei das Werk zu erwähnen aus. Gib danach die Emojis aus. 
Gib danach ein JSON-Schlüssel-Wert-Paar aus. Schlüssel NAME, Wert Name des Werkes. 
Beispiel: Ich habe mir ein Werk ausgedacht, schaffst du es, es zu erraten?\n🔔🏃‍♂️🥊🏟️❤️ {"WorkTitle":"Rocky"}
Nun wähle dein Werk und gib dann deine Antwort ohne den Namen des Werks und das beschriebene JSON aus:
'''

emoji_game_action = {
    'description': 'Emoji-Game spielen',
    'react_to': ['emojis','emoji'],
    'example_user': 'Spielen wir Emojis',
    'example_assistant': 'Okay, ich hab mir etwas überlegt. Rate mal, um welches Werk es sich wohl hierbei handelt: 🧝‍♂️🧙‍♂️🗡️💍🌋  {"WorkTitle": "Der Herr der Ringe"}',
    'key_description': 'WorkTitle und Emojis',
    'value_description': 'Titel des Werks und die Emojis',
    'keys': ['WorkTitle', 'Emojis'],
    'instructions' : 'Schreibe deine Antwort ohne dabei das Werk zu erwähnen aus. Schreibe danach das JSON.'
}

class EmojiGamesModule(JsonActionProviderModule_IF):

    def __init__(self) -> None:
        self.actions = [emoji_game_action]
        self.title_to_guess = ''
        # self.emoji_game_active = False

    def on_keywords_in_input(self, 
            message: LinguFlexMessage,
            keywords_in_input: str) -> None: 
        if 'emoji' in keywords_in_input:
            message.prompt += emoji_game_prompt

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            if 'Game' in json.keys() and json['Game'] == 'Stop':
                self.emoji_game_active = False

            if 'WorkTitle' in json.keys():
                self.title_to_guess = json['WorkTitle']

        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [games] ERROR:' + e)