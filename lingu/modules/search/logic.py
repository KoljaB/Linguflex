from googleapiclient.discovery import build
from PIL import Image, UnidentifiedImageError
from typing import Any, Dict, List
from lingu import cfg, log, Logic
from io import BytesIO
import requests

api_key = cfg("google_api_key", env_key="GOOGLE_API_KEY")
cse_id = cfg("google_cse_id", env_key="GOOGLE_CSE_ID")
no_api_key_msg = \
    "Can't perform that action, Google API Credentials Key and "
"Google Custom Search Engine ID is needed."


class SearchLogic(Logic):
    """
    Logic class for handling text and image search using the Google Search API
    """
    def init(self):
        """Initializes the SearchLogic class."""
        self.search_engine = None
        self.k: int = 10
        self.siterestrict: bool = False
        self.num_results: int = 6

        if not api_key or not cse_id:
            log.err(
                "[search] Missing Google Google API Credentials Key\n"
                " or Google Custom Search Engine ID.\n"
                "  Create a api key at https://console.developers.google.com/"
                " and enable YouTube Data API v3.\n"
                "  Create a search engine id at https://cse.google.com/cse/all"
                " and select 'Search the entire web'.\n"
                "  Write this keys into the 'settings.yaml' file or"
                " set 'GOOGLE_API_KEY' and 'GOOGLE_CSE_ID' environment"
                " variables."
            )
            self.state.set_disabled(True)
        else:
            self.search_engine = build(
                "customsearch",
                "v1",
                developerKey=api_key)

        self.ready()

    def search(self, search_term: str) -> str:
        """
        Searches the internet for information based on the search term.

        Args:
            search_term (str): The search term to search the internet for.

        Returns:
            str: The search results.
        """
        if not self.search_engine:
            return no_api_key_msg

        log.dbg(f"  [search] www search for: {search_term}")
        return {
            "snippets": self.run(search_term),
            "metadata_results": self.results(search_term)
        }

    def search_image(self, search_terms: str):
        if not self.search_engine:
            return no_api_key_msg

        params = {
            "q": search_terms,
            "num": 10,
            "start": 1,
            "imgSize": "large",
            "searchType": "image",
            "key": api_key,
            "cx": cse_id,
        }
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params
        )

        response_data = response.json()

        if response.status_code != 200:
            log.wrn("  [search] request to google custom search API failed,"
                    f" HTTP status code: {response.status_code},"
                    f" answer: {response_data}")
            return None

        if "items" not in response_data:
            log.wrn("  [search] No results found."
                    f" answer: {response_data}")
            return None

        for item in response_data["items"]:
            try:
                image_info = {
                    "image_url": item["link"],
                    "context_link": item.get("image", {}).get("contextLink"),
                    "title": item.get("snippet"),
                    "thumbnail_link": item.get("image", {}).get("thumbnailLink")
                }

                image_response = requests.get(image_info["image_url"])
                img = Image.open(BytesIO(image_response.content))
                image_info["img"] = img
                return image_info
            except UnidentifiedImageError:
                log.dbg("  [search] error retrieving picture of"
                        f" {image_info['image_url']}")
                continue

        return None

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

    def _google_search_results(
            self,
            search_term: str, **kwargs: Any
            ) -> List[dict]:

        cse = self.search_engine.cse()

        if self.siterestrict:
            cse = cse.siterestrict()

        res = cse.list(
            q=search_term,
            cx=cse_id, **kwargs).execute()

        return res.get("items", [])


logic = SearchLogic()
