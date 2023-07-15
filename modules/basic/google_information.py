from core import ActionModule, cfg, log, DEBUG_LEVEL_MIN, DEBUG_LEVEL_MID, DEBUG_LEVEL_MAX, DEBUG_LEVEL_ERR
from linguflex_functions import LinguFlexBase, linguflex_function

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Extra, root_validator, Field
import os

class GoogleSearch(BaseModel):
    """Wrapper for Google Search API."""

    search_engine: Any
    google_api_key: Optional[str] = None
    google_cx_key: Optional[str] = None
    k: int = 10
    siterestrict: bool = False
    num_results: int = 6

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""

        google_api_key = cfg('api_key', 'GOOGLE_API_KEY', section='google_information')
        values["google_api_key"] = google_api_key

        google_cx_key = cfg('cx_key', 'GOOGLE_CX_KEY', section='picture_search')
        values["google_cx_key"] = google_cx_key

        try:
            from googleapiclient.discovery import build

        except ImportError:
            raise ImportError(
                "google-api-python-client is not installed. "
                "Please install it with `pip install google-api-python-client`"
            )

        service = build("customsearch", "v1", developerKey=google_api_key)
        values["search_engine"] = service

        return values

    def _google_search_results(self, search_term: str, **kwargs: Any) -> List[dict]:
        cse = self.search_engine.cse()
        if self.siterestrict:
            cse = cse.siterestrict()
        res = cse.list(q=search_term, cx=self.google_cx_key, **kwargs).execute()
        return res.get("items", [])

    def search(self, query: str) -> str:
        return {
            "snippets": self.run(query),
            "metadata_results" : self.results(query)
        }

    def run(self, query: str) -> str:
        """Run query through GoogleSearch and parse result."""
        snippets = []
        results = self._google_search_results(query, num=self.k)
        if len(results) == 0:
            return "No good Google Search Result was found"
        for result in results:
            if "snippet" in result:
                snippets.append(result["snippet"])

        return snippets

    def results(self, query: str) -> List[Dict]:
        """Run query through GoogleSearch and return metadata."""
        metadata_results = []
        results = self._google_search_results(query, num=self.num_results)
        if len(results) == 0:
            return [{"Result": "No good Google Search Result was found"}]
        for result in results:
            metadata_result = {
                "title": result["title"],
                "link": result["link"],
            }
            if "snippet" in result:
                metadata_result["snippet"] = result["snippet"]
            metadata_results.append(metadata_result)

        return metadata_results
    

gs = GoogleSearch()

class search_world_wide_web(LinguFlexBase):
    "Retrieves real-time information about current events with google search api from the internet"
    search_term: str = Field(..., description="Suitable keywords to achieve optimal search engine results which will help answer the query.")

    def execute(self):
        return gs.search(self.search_term)
    
class AddLocalTime(ActionModule):
    def on_function_added(self, request, name, caller, type):
        self.server.add_time(request)