import logging
import os
import re
from typing import List

from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

from graphing.ui.datas import iso_codes, trend_buttons


def trend_to_human_readable(trend: str) -> str:
    """
    Remove underscores from string and apply uppercase.

    Args:
        trend (str): String to process.
    """
    return trend.replace('_', ' ').upper()


def remove_user_data(update: Update, context: CallbackContext) -> None:
    """
    Remove stored data for that particular user.
    """
    # Commented out in case we need to delete specific items from user_data only-
    # for data in {'covid_country', 'covid_trend_pic', 'log', 'trend_data', 'country_list', 'country_page', 'graph_id'}:
    #     del context.user_data[data]
    #     logging.info(f"Deleted {data} for {update.effective_user.name}!\n")
    del_pic_local(context)

    context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id, message_id=context.user_data['graph_id'],
                                          reply_markup=None)
    logging.info(f"The /graphs markup for {update.effective_user.name} has been removed!\n\n")

    context.user_data.clear()
    trend_buttons[0][-1].text = "Log scale ❌"  # Reset to show False if user timed out in log scale True

    context.dispatcher.persistence.flush()  # Force save

    logging.info(f"All data for {update.effective_user.name} is deleted!\n\n")


def remove_all_user_data(context: CallbackContext) -> None:
    """
    Remove all stored user data.
    """
    del_pic_local(context)

    for user in context.dispatcher.user_data.values():
        user.clear()

    context.dispatcher.persistence.flush()  # Force save
    logging.info(f"All data for all users is deleted!\n\n")


def del_pic_local(context: CallbackContext) -> None:
    """
    Delete the picture which matplotlib stored.
    """
    try:
        os.remove(path=f"graphing/{context.user_data['covid_trend_pic']}.png")
    except (FileNotFoundError, TypeError, KeyError):
        pass


def generate_country_list() -> List[List[List[InlineKeyboardButton]]]:
    """
    Make the country list and separate them into 9 pages. Each page contains 2 columns, 10 rows for a total
    of 20 buttons (i.e countries).
    """
    country_pages = []
    country_list = []
    col = []

    rows = 0

    # Makes one page-
    # country_pages = [[InlineKeyboardButton(text=country, callback_data=iso) for (country, iso), col in
    #                   zip(iso_codes.items(), range(columns))] for row in range(rows)]

    # Makes all pages-

    for iso_code, country in iso_codes.items():
        col.append(InlineKeyboardButton(text=country, callback_data=iso_code))

        if len(col) == 2:
            country_list.append(col)
            rows += 1
            col = []

        if rows == 10:
            rows = 0
            country_pages.append(country_list)
            country_list = []
    else:
        country_pages.append(country_list)

    return country_pages


# def verify_country_list(a=generate_country_list):
#     l = a()
#     counter = 0
#     for element in l:
#         for sub in element:
#             for sub_2 in sub:
#                 print(sub_2.text)
#                 counter += 1
#     assert counter == len(iso_codes), f"Counted: {counter}, Actual: {len(iso_codes)}"


def rolling_avg(data: List[float], average_days: int) -> list:
    """
    Calculate the rolling average of the data provided.

    Args:
        data (list): Data which contains float or integers to calculate the rolling average of.
        average_days (int): Number to average out of.
    """
    total = 0
    result = [0 for _ in data]

    for i in range(0, average_days):
        total = total + data[i]
        result[i] = total / (i + 1)

    for i in range(average_days, len(data)):
        total = total - data[i - average_days] + data[i]
        result[i] = total / average_days

    return result


def remove_emojis(text: str) -> str:
    """
    Remove emojis from given string using regex.

    Args:
        text (str): The text to remove the emoji(s) from.
    """
    pattern = re.compile(pattern="["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                 u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                 "]+", flags=re.UNICODE)
    return pattern.sub(r'', text)
