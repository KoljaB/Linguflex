from core import cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase
from pydantic import Field
from typing import Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import requests

api_key = cfg('api_key', 'GOOGLE_API_KEY')
cx_key = cfg('cx_key', 'GOOGLE_CX_KEY')
 
class search_for_picture(LinguFlexBase):
    "Searches for a picture in the www and displays it"
    search_terms: str = Field(..., description="Search terms for a web search for the picture")

    def execute(self):
        img, image_url = find_relevant_image_by_web_searching_search_terms(self.search_terms)
        if img: img.show()
        return {
            "result" : "picture successfully found and displayed",
            "url" : image_url
        }
    
    

def find_relevant_image_by_web_searching_search_terms(search_terms: str) -> Optional[Image.Image]:
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
            return img, image_url
        except UnidentifiedImageError:
            log(DEBUG_LEVEL_MAX, f'  [showpicture] could not identify picture of {image_url}, trying next picture')
            continue
    return None