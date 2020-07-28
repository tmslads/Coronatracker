import logging

from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

from graphing.ui.datas import iso_codes


def trend_to_human_readable(trend: str) -> str:
    return trend.replace('_', ' ').upper()


def remove_user_data(update: Update, context: CallbackContext) -> None:
    # Commented out in case we need to delete specific items from user_data only-
    # for data in {'covid_country', 'covid_trend_pic', 'log', 'trend_data', 'country_list', 'country_page'}:
    #     del context.user_data[data]
    #     logging.info(f"Deleted {data} for {update.effective_user.full_name}!\n")
    context.user_data.clear()
    logging.info(f"All data for {update.effective_user.full_name} is deleted!\n\n")


def remove_all_user_data(context: CallbackContext) -> None:
    # print(context.dispatcher.user_data.values())
    for user in context.dispatcher.user_data.values():
        user.clear()
    logging.info(f"All data for all users is deleted!\n\n")


def generate_country_list():
    country_pages = []
    country_list = []
    col = []

    rows = 0
    columns = 0

    # Makes one page-
    # country_list = [[InlineKeyboardButton(text=country, callback_data=iso) for (country, iso), col in
    #                  zip(iso_codes.items(), range(columns))] for row in range(rows)]

    # Makes all pages-
    for iso_code, country in iso_codes.items():
        if rows < 10:
            if columns < 2:
                col.append(InlineKeyboardButton(text=country, callback_data=iso_code))
                columns += 1
            else:
                country_list.append(col)
                columns = 0
                rows += 1
                col = []
        else:
            rows = 0
            columns = 0
            country_pages.append(country_list)
            country_list = []
    else:
        country_pages.append(country_list)

    return country_pages


# def verify_list(a=generate_country_list):
#     l = a()
#     for element in l:
#         for sub in element:
#             for sub_2 in sub:
#                 print(sub_2.text)


def rolling_avg(data: list, average_days: int) -> list:
    total = 0
    result = [0 for _ in data]

    for i in range(0, average_days):
        total = total + data[i]
        result[i] = total / (i + 1)

    for i in range(average_days, len(data)):
        total = total - data[i - average_days] + data[i]
        result[i] = total / average_days

    return result
