import sys
sys.path.insert(0, '..')
import os
import requests

from linguflex_interfaces import JsonActionProviderModule_IF
from linguflex_log import log, DEBUG_LEVEL_OFF, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX
from linguflex_config import cfg, set_section, get_section, configuration_parsing_error_message
from linguflex_message import LinguFlexMessage
from typing import Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO

set_section('openai_generator')

API_KEY_NOT_FOUND_ERROR_MESSAGE = 'OpenAI API-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_OPENAI_API_KEY.'

# Import OpenAI API-Key from either registry (LINGU_OPENAI_API_KEY) or config file openai_generator/openai_api_key
api_key = os.environ.get('LINGU_OPENAI_API_KEY')
if api_key is None:
    try:
        api_key = cfg[get_section()]['openai_api_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if api_key is None:
    raise ValueError(API_KEY_NOT_FOUND_ERROR_MESSAGE)

generate_picture_action = {
    'description': 'Bilder mit DALL·E 2 erzeugen',
	'react_to': ['bild', 'bilder', 'gemälde', 'erzeuge', 'erzeug', 'erstelle', 'kreiere', 'kreier', 'schaffe', 'erschaffe', 'illustration', 'grafik', 'zeichnung', 'foto', 'fotografie', 'entwerfe', 'entwurf', 'design', 'gestalte', 'gestaltung', 'kunstwerk', 'kunst', 'visuell', 'visuelle', 'visualisierung', 'skizze', 'skizzieren', 'collage', 'konzept', 'konzeption', 'darstellung', 'abbildung', 'muster', 'motiv', 'komposition'],
    'example_user': 'Male mir ein Bild von einem Eichhörnchen, das in Bier schwimmt',
    'example_assistant': 'Hier ist ein Gemälde eines Eichhörnchens in Ölfarben {"GeneratePic":"Ölfarbengemälde eines in Bier badenden Eichhörnchen."}',
    'key_description': '"GeneratePic"',
    'value_description': 'Geeignete Stichwort(e) für die Bilderzeugung mit OpenAI DALL·E 2',
    'keys': ['GeneratePic'],
    'instructions' : 'Überlege ein kreatives Prompt zur Erzeugung eines optimal zur Anfrage passendes Bilds'
}

class JV_Dalle(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [generate_picture_action]

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            img = self.generate_image(json['GeneratePic'])            

            if img:
                img.show()
                log(DEBUG_LEVEL_MID, f'[dalle] showing picture')       
            else:
                log(DEBUG_LEVEL_MID, f'[dalle] no picture found')       
            #find_relevant_image_by_web_searching_search_terms
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [dalle] ERROR:' + e)

    def generate_image(self, prompt: str) -> Optional[Image.Image]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }        
        data = {
            "model": "image-alpha-001",
            "prompt": prompt,
            "num_images": 1,
            "size": "1024x1024",
            "response_format": "url"
        }        
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)
        response_data = response.json()        
        if response.status_code != 200:
            log(DEBUG_LEVEL_MIN, f'  [generatepicture] request to OpenAI image generations API failed, HTTP status code: {response.status_code}')
            log(DEBUG_LEVEL_MIN, f'  [generatepicture] answer: {response_data}')
            return None        
        if "data" not in response_data or len(response_data["data"]) == 0:
            log(DEBUG_LEVEL_MID, f' [generatepicture] No results found.')
            log(DEBUG_LEVEL_MID, f' [generatepicture] answer: {response_data}')
            return None
        image_url = response_data["data"][0]["url"]
        try:
            image_response = requests.get(image_url)
            img = Image.open(BytesIO(image_response.content))
            return img
        except UnidentifiedImageError:
            log(DEBUG_LEVEL_MAX, f'  [generatepicture] could not identify generated picture')
            return None