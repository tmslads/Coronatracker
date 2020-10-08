import re

import requests
from bs4 import BeautifulSoup as bs

GULFNEWS_URL = "https://gulfnews.com"


class GulfNews(object):
    def __init__(self):
        get = requests.get(GULFNEWS_URL, timeout=100)
        self.soup = bs(get.content, features='html.parser')

    def breaking(self):
        latest_breaking = self.soup.find_all(class_='card-title')

        for breaking in latest_breaking:
            title = breaking.a.get_text().strip().replace('  ', ' ')
            pattern1 = re.compile("\A(UAE|Coronavirus: UAE|COVID(-|\s)*19: UAE) (announces|reports|reported) ([0-9,]+) "
                                  "(new (coronavirus*) cases)*.*")
            pattern2 = re.compile("(\d+) new cases of COVID-19 (UAE)*")
            if re.search(pattern=pattern1, string=title) or re.search(pattern=pattern2, string=title):
                breaking_link = breaking.a['href']
                return f"{GULFNEWS_URL + breaking_link}"  # Send link to breaking article


# FOR TRAINING THE REGEX:
# news_headlines = ["COVID 19: UAE announces 4 deaths, 518 new coronavirus cases and 91 recoveries",
#                   "UAE announces 490 new coronavirus cases, 6 deaths",
#                   "UAE announces 483 new coronavirus cases, six deaths",
#                   "UAE announces 490 new coronavirus cases, three deaths",
#                   "COVID 19: UAE announces 484 new coronavirus cases",
#                   "COVID 19: UAE announces 4 deaths, 479 new cases",
#                   "UAE announces 2 deaths, 477 new coronavirus cases and 97 recoveries on Friday",
#                   "UAE announces 2 deaths and 61 recoveries", "UAE announces 460 new coronavirus cases on Thursday",
#                   "UAE announces 5 deaths, 432 new cases and 101 recoveries on Thursday",
#                   "COVID 19: UAE announces 412 new coronavirus cases", "COVID-19: UAE announces 398 new cases",
#                   "COVID-19: UAE announces 3 deaths, 172 recoveries",
#                   "COVID-19: UAE announces 387 new coronavirus cases.",
#                   "Coronavirus: UAE reports 331 new COVID-19 cases, 2 deaths", "UAE reports 27 new coronavirus cases",
#                   "Coronavirus: UAE announces activation of remote work for government and private sector",
#                   "UAE announces $2 billion aid for Mauritania", "UAE announces ninth case of coronavirus",
#                   "UAE announces 6-month interim visas for long-term residence visa seekers",
#                   "UAE announces 14 new coronavirus cases"]
