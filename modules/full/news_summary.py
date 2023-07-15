from linguflex_functions import LinguFlexBase
from news_summary_helper import NewsParser
from pydantic import Field
import enum

class NewsTopic(str, enum.Enum):
    """Enumeration representing the news topic to retrieve"""

    MAINNEWS = "mainnews"
    TECHNOLOGY = "technology"
    ECONOMY = "economy"
    RESEARCH = "research"
    DOMESTIC = "domestic"
    INTERNATIONAL = "international"
    SOCIETY = "society"

class retrieve_current_news(LinguFlexBase):
    "Retrieve news about a given topic"
    topic: NewsTopic = Field(..., description="News topic to retrieve information on")

    def execute(self):
        if self.topic == 'technology':
            return NewsParser().get_technik_summarization()
        elif self.topic == 'economy':
            return NewsParser().get_economy_summarization()
        elif self.topic == 'research':
            return NewsParser().get_forschung_summarization()
        elif self.topic == 'domestic':
            return NewsParser().get_inland_summarization()
        elif self.topic == 'international':
            return NewsParser().get_ausland_summarization()
        elif self.topic == 'society':
            return NewsParser().get_gesellschaft_summarization()
        else:
            return NewsParser().get_main_summarization()