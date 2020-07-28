import logging
import sqlite3
from datetime import datetime

import pandas as pd
import requests
from telegram.ext import CallbackContext


class DataHandler:

    def __init__(self, iso: str = None):
        self.conn = sqlite3.connect('graphing/covid_data.db')
        self.c = self.conn.cursor()

        self.iso = iso

    def convert_to_sql(self):
        df = pd.read_csv('graphing/owid-covid-data.csv')
        pd.DataFrame.to_sql(df, name='world_covid_data', con=self.conn, if_exists='replace')
        logging.info('Converted to sqlite database!')

    def query(self, query: str):
        """Executes the given query and returns it."""
        return self.c.execute(query)

    def case_data(self, _type: str):
        if 'new' in _type:
            result = self.c.execute(f"SELECT date, {_type} from world_covid_data where new_cases >= 1 and "
                                    f"iso_code='{self.iso}' and total_cases is not null;")
        else:
            result = self.c.execute(f"SELECT date, {_type} from world_covid_data where "
                                    f"iso_code='{self.iso}' and total_cases is not null;")

        return self.converter_n_splitter(result.fetchall(), split=True)

    def death_data(self, _type: str):
        result = self.c.execute(f"SELECT date, {_type} from world_covid_data where iso_code='{self.iso}';")
        return self.converter_n_splitter(result.fetchall(), split=True)

    @staticmethod
    def converter_n_splitter(data, split: bool = False):
        dates = []
        other_data = []

        for index, entry in enumerate(data[:]):
            data[index] = list(entry)
            data[index][0] = datetime.strptime(entry[0], "%Y-%m-%d")

            if split:
                dates.append(data[index][0])
                other_data.append(data[index][1])

        return data if not split else (dates, other_data)


def download_file(context: CallbackContext):
    if 'last_data_dl_date' not in context.bot_data:
        context.bot_data['last_data_dl_date'] = datetime.today()

    today = datetime.today()
    dl_today = context.bot_data['last_data_dl_date']

    if (today - dl_today).seconds < 21600:  # Update if more than 6 hours have passed.
        logging.info("Not time for updates yet.")
        del today, dl_today
        return

    logging.info("Beginning to download...")

    r = requests.get("https://covid.ourworldindata.org/data/owid-covid-data.csv", allow_redirects=True)
    open("graphing/owid-covid-data.csv", 'wb').write(r.content)

    logging.info("Downloaded and written to file!")

    logging.info("Converting to sqlite database...")
    DataHandler().convert_to_sql()

    context.bot_data['last_data_dl_date'] = datetime.today()
    logging.info("Last data get date updated!")
