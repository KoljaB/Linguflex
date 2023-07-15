from bs4 import BeautifulSoup
from requests import get
from urllib.parse import urljoin
import json

max_chars = 8000
max_articles = 3

class NewsParser:
    """
    A class to parse news from a specific HTML format.
    """
    baseurl = 'https://www.tagesschau.de/'

    economy_url = 'wirtschaft/finanzen/marktberichte'
    inland_url = 'inland'
    ausland_url = 'ausland'
    technik_url = 'wissen/technologie'
    forschung_url = 'wissen/forschung'
    gesellschaft_url = 'inland/gesellschaft'
    
    @staticmethod
    def get_news_info(html):
        """
        Parses an HTML string to extract news information.

        Returns the article body as a string.
        """
        soup = BeautifulSoup(html, 'html.parser')
        script = soup.find('script', type='application/ld+json')
        data = json.loads(script.string)
        return data['articleBody']

    @classmethod
    def get_economy_summarization(self):
        return self.get_news_summarization(self.economy_url)

    @classmethod
    def get_inland_summarization(self):
        return self.get_news_summarization(self.inland_url)

    @classmethod
    def get_ausland_summarization(self):
        return self.get_news_summarization(self.ausland_url)

    @classmethod
    def get_technik_summarization(self):
        return self.get_news_summarization(self.technik_url)

    @classmethod
    def get_forschung_summarization(self):
        return self.get_news_summarization(self.forschung_url)

    @classmethod
    def get_gesellschaft_summarization(self):
        return self.get_news_summarization(self.gesellschaft_url)

    @classmethod
    def get_main_summarization(self):
        return self.get_news_summarization('')

    @classmethod
    def get_news_summarization(self, suburl):
        joined_url = urljoin(self.baseurl, suburl)
        response = get(joined_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        teaser_headlines = soup.find_all('span', {'class': 'teaser__headline'})

        articles = []
        for i in range(max_articles):  # Get the first articles
            parent_teaser_link = teaser_headlines[i].find_parent('a', {'class': 'teaser__link'})
            full_link = urljoin(self.baseurl, parent_teaser_link['href'])
            response = get(full_link)
            article = self.get_news_info(response.text)
            articles.append(article)

        while sum(len(a) for a in articles) > max_chars:
            # Find the longest article
            longest_article = max(articles, key=len)
            # Remove one character from the longest article
            articles[articles.index(longest_article)] = longest_article[:-1]

        return articles