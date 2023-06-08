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

set_section('pic_search')

API_KEY_NOT_FOUND_ERROR_MESSAGE = 'Google Custom Search API-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_GOOGLE_API_KEY.'
CX_KEY_NOT_FOUND_ERROR_MESSAGE = 'Google Custom Search CX-Key not found. Please define the key in your linguflex config file or set the key in the environment variable LINGU_GOOGLE_CX_KEY.'

# Import Google API-Key from either registry (LINGU_GOOGLE_API_KEY) or config file jv_pic/google_api_key
api_key = os.environ.get('LINGU_GOOGLE_API_KEY')
if api_key is None:
    try:
        api_key = cfg[get_section()]['google_api_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if api_key is None:
    raise ValueError(API_KEY_NOT_FOUND_ERROR_MESSAGE)

# Import Google CX-Key from either registry (LINGU_GOOGLE_CX_KEY) or config file jv_pic/google_cx_key
cx_key = os.environ.get('LINGU_GOOGLE_CX_KEY')
if cx_key is None:
    try:
        cx_key = cfg[get_section()]['google_cx_key']
    except Exception as e:
        raise ValueError(configuration_parsing_error_message + ' ' + str(e))
if cx_key is None:
    raise ValueError(CX_KEY_NOT_FOUND_ERROR_MESSAGE)

show_picture_action = {
    'description': 'Bilder im Internet suchen und anzeigen',
    'react_to': ['bild', 'bilder', 'zeig', 'zeige', 'suche', 'foto', 'fotos', 'darstellen', 'präsentieren', 'anzeigen', 'abbildung', 'abbildungen', 'grafik', 'grafiken', 'fotografie', 'fotografien', 'illustration', 'illustrationen', 'visuell', 'visualisieren', 'image', 'images', 'pic', 'pics', 'aufnahme', 'aufnahmen'],
    'example_user': 'Zeig mir ein Bild vom Eiffelturm',
    'example_assistant': 'Hier ist ein Bild vom Eiffelturm {"ShowPic":"Eiffelturm"}',
    'key_description': '"ShowPic"',
    'value_description': 'Stichwort(e) für das Bild',
    'keys': ['ShowPic'],
    'instructions' : ''
}

class JV_Pic(JsonActionProviderModule_IF):
    def __init__(self) -> None:
        self.actions = [show_picture_action]

    def perform_action(self, 
            message: LinguFlexMessage,
            json) -> None:
        try:
            img = self.find_relevant_image_by_web_searching_search_terms(json['ShowPic'])

            if img:
                img.show()
                log(DEBUG_LEVEL_MID, f'[showpicture] showing picture')       
            else:
                log(DEBUG_LEVEL_MID, f'[showpicture] no picture found')       
            #find_relevant_image_by_web_searching_search_terms
        except Exception as e:
            log(DEBUG_LEVEL_MIN, '  [showpicture] ERROR:' + e)

    def find_relevant_image_by_web_searching_search_terms(self,
            search_terms: str) -> Optional[Image.Image]:
        params = {
            "q": search_terms,
            "num": 10,
            "start": 1,
            "imgSize": "large",
            "searchType": "image",
            "key": api_key,
            "cx": cx_key,
        }        
        response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
        response_data = response.json()        
        if response.status_code != 200:
            log(DEBUG_LEVEL_MIN, f'  [showpicture] request to google custom search API failed, HTTP status code: {response.status_code}')
            log(DEBUG_LEVEL_MIN, f'  [showpicture] answer: {response_data}')
            return None        
        if "items" not in response_data:
            log(DEBUG_LEVEL_MID, f'  [showpicture] No results found.')
            log(DEBUG_LEVEL_MID, f'  [showpicture] answer: {response_data}')
            return None
        for item in response_data["items"]:
            image_url = item["link"]
            try:
                image_response = requests.get(image_url)
                img = Image.open(BytesIO(image_response.content))
                return img
            except UnidentifiedImageError:
                log(DEBUG_LEVEL_MAX, f'  [showpicture] could not identify picture of {image_url}, trying next picture')
                continue
        return None        