from IPython.utils import io
from serpapi import GoogleSearch
import re

url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

class GoogleSearchAPI:
    '''
    A class to perform Google search via the Serpapi API

    Attributes:
    serpapi_key (str): API key to use the Serpapi service
    '''

    def __init__(self, 
            serpapi_key: str) -> None:
        '''
        Initializes GoogleSearchAPI with the specified Serpapi API key.
        '''
        self.serpapi_key = serpapi_key

    def process_response(self, 
            res: dict) -> str:
        '''
        Process response from SerpAPI, shamelessly stolen from langchain.
        '''
        if 'error' in res.keys():
            raise ValueError(f'Got error from SerpAPI: {res["error"]}')
        if 'answer_box' in res.keys() and 'answer' in res['answer_box'].keys():
            toret = res['answer_box']['answer']
        elif 'answer_box' in res.keys() and 'snippet' in res['answer_box'].keys():
            toret = res['answer_box']['snippet']
        elif (
            'answer_box' in res.keys()
            and 'snippet_highlighted_words' in res['answer_box'].keys()
        ):
            toret = res['answer_box']['snippet_highlighted_words'][0]
        elif (
            'sports_results' in res.keys()
            and 'game_spotlight' in res['sports_results'].keys()
        ):
            toret = res['sports_results']['game_spotlight']
        elif (
            'sports_results' in res.keys()
            and 'games' in res['sports_results'].keys()
        ):
            toret = res['sports_results']['games']
        elif (
            'local_results' in res.keys()
            and 'places' in res['local_results'].keys()
        ):
            toret = res['local_results']['places']
        elif (
            'knowledge_graph' in res.keys()
            and 'description' in res['knowledge_graph'].keys()
        ):
            toret = res['knowledge_graph']['description']
        elif 'snippet' in res['organic_results'][0].keys():
            toret = res['organic_results'][0]['snippet']

        else:
            toret = 'Leider keine passendes Suchergebnis von Google.'
        return toret       

    def remove_links_from_dict(self, d):    
        for key, value in d.items():
            if isinstance(value, str):
                d[key] = re.sub(url_pattern, '', value)
            elif isinstance(value, dict):
                d[key] = self.remove_links_from_dict(value)
            elif isinstance(value, list):
                d[key] = self.remove_links_from_list(value)
        
        return d

    def remove_links_from_list(self, lst):
        for i, item in enumerate(lst):
            if isinstance(item, str):
                lst[i] = re.sub(url_pattern, '', item)
            elif isinstance(item, dict):
                lst[i] = self.remove_links_from_dict(item)
            elif isinstance(item, list):
                lst[i] = self.remove_links_from_list(item)
        
        return lst

    def remove_links(self, input_data):
        if isinstance(input_data, str):
            return re.sub(url_pattern, '', input_data)
        elif isinstance(input_data, dict):
            return self.remove_links_from_dict(input_data)
        elif isinstance(input_data, list):
            return self.remove_links_from_list(input_data)
        else:
            raise TypeError("Unsupported data type")    
    
    def optimize(self,
            input_data: str) -> str:
        '''
        Replaces unneeded stuff to save tokens
        '''
        output_data = input_data.replace(", 'thumbnail': ''", "")
        output_data = output_data.replace("': '", "':'")
        output_data = output_data.replace("', '", "','")
        output_data = output_data.replace("}, {", "},{")
            
        return output_data    

    def search(self, 
            query: str) -> str:
        '''
        Performs a Google search using the Serpapi API.

        Args:
        query (str): The search query.

        Returns:
        str: The first search result text or None if no result found.
        '''
        # https://serpapi.com/search-api
        params = {
            'api_key': self.serpapi_key,    # https://serpapi.com/search-api#api-parameters-serpapi-parameters-api-key
            'engine': 'google',             # https://serpapi.com/search-api#api-parameters-serpapi-parameters-engine
            'q': query,                     # https://serpapi.com/search-api#api-parameters-search-query-q                  https://serpapi.com/advanced-google-query-parameters
            'google_domain': 'google.de',   # https://serpapi.com/search-api#api-parameters-serpapi-parameters-api-key      https://serpapi.com/google-domains
            'gl': 'de',                     # https://serpapi.com/search-api#api-parameters-localization-gl                 https://serpapi.com/google-countries
            'hl': 'de'                      # https://serpapi.com/search-api#api-parameters-localization-hl                 https://serpapi.com/google-languages
        }

        with io.capture_output() as captured: # disables prints from GoogleSearch
            search = GoogleSearch(params)
            res = search.get_dict()
        
        response = self.process_response(res)
        response_no_links = self.remove_links(response)
        optimized = self.optimize(str(response_no_links))

        return optimized
    
        # if 'answer_box' in res.keys() and 'answer' in res['answer_box'].keys():
        #     return res['answer_box']['answer']
        # elif 'answer_box' in res.keys() and 'snippet' in res['answer_box'].keys():
        #     return res['answer_box']['snippet']
        # elif 'answer_box' in res.keys() and 'snippet_highlighted_words' in res['answer_box'].keys():
        #     return res['answer_box']["snippet_highlighted_words"][0]
        # elif 'snippet' in res["organic_results"][0].keys():
        #     return res["organic_results"][0]['snippet']
        # else:
        #     return 'Leider keine passendes Suchergebnis von Google.'