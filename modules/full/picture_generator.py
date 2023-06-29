from core import cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase
from pydantic import Field
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from typing import Optional
import requests

api_key = cfg('api_key', 'OPENAI_API_KEY')

class create_picture_with_dalle(LinguFlexBase):
    "Creates and displays image with DALL-E 2 from a prompt, which should describe in detail how the picture could look"
    prompt: str = Field(..., description="Detailled description in natural language about how the picture should look")

    def execute(self):
        img, image_url = generate_image(self.prompt)
        if img: img.show()
        return {
            "result" : "picture successfully created and displayed",
            "url" : image_url
        }

def generate_image(prompt: str) -> Optional[Image.Image]:
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
        log(DEBUG_LEVEL_ERR, f'  [generatepicture] dalle request failed, HTTP status code: {response.status_code}, answer: {response_data}')
        return None        
    if "data" not in response_data or len(response_data["data"]) == 0:
        log(DEBUG_LEVEL_ERR, f' [generatepicture] no results found, answer: {response_data}')
        return None
    image_url = response_data["data"][0]["url"]
    try:
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
        return img, image_url
    except UnidentifiedImageError:
        log(DEBUG_LEVEL_ERR, f'  [generatepicture] could not identify generated picture')
        return None