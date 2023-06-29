from core import ActionModule, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function
from pydantic import Field
from google_information_helper import GoogleSearchAPI
from datetime import datetime, timedelta

api_key = cfg('api_key', 'SERP_API_KEY')
google = GoogleSearchAPI(api_key)

class search_world_wide_web(LinguFlexBase):
    "Retrieves real-time information about current events from the internet"
    search_term: str = Field(..., description="Suitable keywords to achieve optimal search engine results which will help answer the query.")

    def execute(self):
        return google.search(self.search_term)
    
class AddLocalTime(ActionModule):
    def on_function_added(self, message, name, type):         
        self.server.add_time(message)