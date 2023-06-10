import requests
from bs4 import BeautifulSoup

class ComdirectInformationParser:
    """
    A class to parse stock information from a specific HTML format.
    """

    def __init__(self, url):
        """
        Initialize the StockParser with a URL to scrape.
        """
        self.url = url

    def parse_stock_info(self, html):
        """
        Parses an HTML string to extract stock information.

        Returns a list of dictionaries, where each dictionary corresponds to a single stock.
        """
        soup = BeautifulSoup(html, 'html.parser')

        stocks_info = []
        rows = soup.select('.alpha.uebersicht tbody tr')

        for row in rows:
            stock = self._parse_row(row)
            stocks_info.append(stock)

        return stocks_info

    def _parse_row(self, row):
        """
        Helper method to parse a single row of the HTML table.

        Returns a dictionary with the parsed stock data.
        """
        stock = {}

        name_td = row.find(class_='left name')
        if name_td:
            name = name_td.a.text.strip()
            short_name = name.split('\u200b', 1)[0] if '\u200b' in name else name
            stock['Name'] = short_name.strip()

        cells = row.find_all('td')

        akt_kurs_diff_abs = cells[5].find_all('span')[2].text.strip()
        akt_kurs_diff_percent = cells[5].find_all('span')[3].text.strip()

        wert_in_eur = cells[6].find_all('span')[0].text.strip()
        wert_diff_abs = cells[6].find_all('span')[2].text.strip()
        wert_diff_percent = cells[6].find_all('span')[3].text.strip()

        stock['Performance Heute'] = self._format_value(akt_kurs_diff_percent)
        stock['Gesamtwert'] = self._format_value(wert_in_eur)
        stock['Performance Gesamt'] = self._format_value(wert_diff_percent)

        return stock

    def _format_value(self, value):
        """
        Helper method to format a value string.
        """
        return value.replace('.', '').replace(',', '.').replace('\xa0', '')

    def get_summarization(self, perform_parse=True):
        """
        Get the summarization of stock information from the specified URL.

        If perform_parse is True, will also parse the individual stock data.
        """
        response = requests.get(self.url)

        soup = BeautifulSoup(response.text, 'html.parser')

        diff_zum_vortag_value = self._extract_value(soup, 'p', 'selectBox floatRight', 'b', ['plus', 'minus'])
        depotwert_value = self._extract_value(soup, 'p', 'kgvMargin floatRight', 'b')

        summarization = f"Differenz zum Vortag: {diff_zum_vortag_value} €\nGesamtwert: {depotwert_value} €\n"

        if perform_parse:
            stocks_info = self.parse_stock_info(response.text)
            summarization += self._format_stock_info(stocks_info)

        return summarization
    
    def _extract_value(self, soup, parent_tag, parent_class, child_tag, child_classes=None):
        """
        Helper method to extract a value from the HTML soup.
        """
        parent_element = soup.find(parent_tag, class_=parent_class)

        if child_classes:  # If child classes are provided
            for child_class in child_classes:
                child_element = parent_element.select_one(f"{child_tag}.{child_class}")
                if child_element:
                    break
        else:
            child_element = parent_element.find(child_tag)

        value_text = child_element.get_text(strip=True)
        value_text = value_text.replace('+', '').replace('EUR', '').replace('.', '').replace(',', '.').replace('\xa0', '')
        value = float(value_text)

        return value    

    def _format_stock_info(self, stocks_info):
        """
        Helper method to format stock information for output.
        """
        stocks_string = "Einzelwerte:\n"
        for stock in stocks_info:
            stocks_string += f"{stock['Name']} | Heute: {stock['Performance Heute']}, Gesamtwert: {stock['Gesamtwert']}€ ({stock['Performance Gesamt']})\n"

        return stocks_string