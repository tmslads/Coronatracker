import requests
from bs4 import BeautifulSoup as bs, NavigableString
from typing import Tuple, List, Dict

URL = "https://www.worldometers.info/coronavirus/"


class WorldMeter(object):
    def __init__(self, country=None):
        self.country = country
        get = requests.get(URL)
        self.soup = bs(get.content, features='html.parser')

    def latest_data(self) -> Tuple[str, str, str]:
        cases = self.soup.find_all(class_='maincounter-number')
        total, dead, recovered = (case.span.string.strip() for case in cases)
        return total, dead, recovered

    def ae_data(self) -> Tuple[Dict[str, str], List[str]]:

        info = self.soup.find_all(href="country/united-arab-emirates/")[0]  # [0] Since get 2 elements for some reason
        siblings = info.parent.next_siblings  # Go up the tree and get its siblings
        new = {'new_cases': '', 'new_deaths': ''}
        totals = []

        for index, sibling in enumerate(siblings):
            string = sibling.string
            if isinstance(string, NavigableString) and string != '\n':
                if '+' in string:
                    if index == 3:
                        new['new_cases'] = str(string)  # Convert to string to save memory!
                    else:
                        new['new_deaths'] = str(string)
                else:
                    totals.append(str(string))

        return new, totals


WorldMeter().ae_data()
