"""
Search Module

- performs text and image search using the Google Search API

"""

from lingu import log, Populatable
from pydantic import Field
from .logic import logic


class SearchWorldWideWeb(Populatable):
    """
    Retrieves real-time information about current events from the internet.
    Uses google search api.
    """
    search_term: str = Field(
        ...,
        description="Suitable keywords to achieve optimal search engine"
        " results which will help answer the query.")

    def on_populated(self):
        return logic.search(self.search_term)


class SearchForPicture(Populatable):
    """
    Searches for a picture in the www and displays it
    """
    search_terms: str = Field(
        ...,
        description="Search terms for a web search for the picture")

    def on_populated(self):
        image_info = logic.search_image(self.search_terms)
        try:
            if image_info and image_info["img"]:
                title = image_info.get("title", "No Title")
                image_info["img"].show(title=title)

                return {
                    "result": "picture successfully found and displayed",
                    "url": image_info["image_url"]
                }
        except Exception as e:
            log.inf(f"  [search] error displaying picture: {str(e)}")
            return {
                "result": "No picture found",
                "error": str(e)
            }
        return {
            "result": "No picture found"
        }
