import logging
import sqlite3
from datetime import datetime
from typing import Union, Tuple, List

import pandas as pd
import requests
from telegram.ext import CallbackContext
from tqdm import tqdm


class DataHandler:
    """Class to handle all database related operations and queries."""

    def __init__(self, iso: str = None):
        self.conn = sqlite3.connect('graphing/covid_data.db')
        self.c = self.conn.cursor()

        self.iso = iso

    def convert_to_sql(self):
        """Convert .csv file to .db file using pandas method."""
        df = pd.read_csv('graphing/owid-covid-data.csv')
        pd.DataFrame.to_sql(df, name='world_covid_data', con=self.conn, if_exists='replace')
        logging.info('Converted to sqlite database!')

    def query(self, query: str):
        """
        Execute the given query and return it.

        Args:
            query (str): The query for requesting to the database.
        """
        return self.c.execute(query)

    def case_data(self, _type: str):
        """
        Fetch covid-19 case data and return it with dates.

        Args:
            _type (str): Name of the column to get test data from. Can be 'new_cases' or 'total_cases'."""
        result = self.c.execute(f"SELECT date, {_type} from world_covid_data where "
                                f"iso_code='{self.iso}' and total_cases is not null;").fetchall()

        return self.converter_n_splitter(result, split=True)

    def death_data(self, _type: str):
        """
        Fetch covid-19 death data and return it with dates.

        Args:
            _type (str): Name of the column to get test data from. Can be 'new_deaths' or 'total_deaths'.
        """
        result = self.c.execute(f"SELECT date, {_type} from world_covid_data where iso_code='{self.iso}';").fetchall()
        return self.converter_n_splitter(result, split=True)

    def tests_data(self, _type: str, with_dates: bool = False):
        """
        Fetch covid-19 test data and return it with dates, if specified.

        Args:
            _type (str): Name of the column to get test data from. Can be 'new_tests' or 'total_tests'.
            with_dates (bool): Pass True, if you want the data to contain dates too. Default: False
        """
        if with_dates:
            query = "date,"
        else:
            query = ""

        result = self.c.execute(f"SELECT {query}{_type} from world_covid_data where iso_code='{self.iso}' "
                                f"and total_cases is not null and tests_units is not null;").fetchall()

        if not result:
            return False

        if with_dates:
            return self.converter_n_splitter(result, split=True)
        else:
            return [0 if obj[0] is None else obj[0] for obj in result]

    def pct_positive(self):
        """
        Fetch covid-19 test & new case data, & use that to find out the % of tests that returned positive on that
        particular day.
        """
        result = self.c.execute(f"SELECT date, (new_cases/new_tests)*100 from world_covid_data where "
                                f"iso_code='{self.iso}' and new_tests > 0 and tests_units is not null;").fetchall()
        if not result:
            return False

        return self.converter_n_splitter(result, split=True)

    @staticmethod
    def converter_n_splitter(data: list, split: bool = False) -> Union[List, Tuple[datetime, int]]:
        """
        Convert all strings into datetime objects, None type objects to 0, and splits the data into tuples if specified.

        Args:
            data (list): The data to process.
            split (bool): Pass True, if you want to split the data into two. Default: False.
        """
        dates = []
        other_data = []

        for index, entry in enumerate(data[:]):
            data[index] = list(entry)  # entry is a tuple

            data[index][0] = datetime.strptime(entry[0], "%Y-%m-%d")

            if split:
                dates.append(data[index][0])

                if data[index][1] is None:
                    data[index][1] = 0

                other_data.append(data[index][1])

        return data if not split else (dates, other_data)


def download_file(context: CallbackContext):
    """
    Download the full covid-19 dataset from ourworldindata every 6 hours. Also shows the download progress bar.

    Args:
        context (CallbackContext): Required context object by python-telegram-bot.
    """
    if 'last_data_dl_date' not in context.bot_data:
        context.bot_data['last_data_dl_date'] = datetime.today()

    today = datetime.today()
    dl_today = context.bot_data['last_data_dl_date']

    if (today - dl_today).seconds < 21600:  # Update if more than 6 hours have passed.
        logging.info("Not time for updates yet.")
        del today, dl_today
        return

    logging.info("Beginning to download...")

    r = requests.get("https://covid.ourworldindata.org/data/owid-covid-data.csv", allow_redirects=True, stream=True,
                     proxies=context.job.context['owid'], timeout=20)
    block_size = 1024

    total_size_in_bytes = (int(r.headers.get('content-length', 0)) / (32 * block_size))

    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

    with open("graphing/owid-covid-data.csv", 'wb') as file:
        for data in r.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

    logging.info("Downloaded and written to file!")

    logging.info("Converting to sqlite database...")
    DataHandler().convert_to_sql()

    context.bot_data['last_data_dl_date'] = datetime.today()
    logging.info("Last data get date updated!")
