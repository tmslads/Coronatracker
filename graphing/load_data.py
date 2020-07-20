import sqlite3
from datetime import datetime

import pandas as pd


class DataHandler:

    def __init__(self):
        self.conn = sqlite3.connect('covid_data.db')
        self.c = self.conn.cursor()

    def convert_to_sql(self):
        df = pd.read_csv('owid-covid-data.csv')
        pd.DataFrame.to_sql(df, name='world_covid_data', con=self.conn, if_exists='replace')
        print('done')

    def query(self, query: str):
        """Executes the given query and returns it."""
        return self.c.execute(query)

    def case_data(self, iso: str, till: str = None, new: str = None):

        result = self.c.execute(f"SELECT date, total_cases from world_covid_data where new_cases >= 1 and "
                                f"iso_code = '{iso}'")
        data = result.fetchall()
        new_data = self.converter_n_splitter(data, split=True)
        return new_data

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


DataHandler().case_data(iso="ARE")
