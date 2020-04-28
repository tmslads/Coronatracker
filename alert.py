import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from helpers.db_connector import connection
from helpers.namer import get_chat_name
from scrapers.gulfnews import GulfNews

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)

text = "This bot can also send you breaking COVID-19 news for the UAE such as new cases, " \
       "deaths, etc. when they come in (usually once a day).\n\n" \
       "Do you wish to opt in to receive such news?\n\n" \
       "Current status is: ()"

alert_button = [[InlineKeyboardButton(text="🔧 Toggle On/Off", callback_data="toggle")]]
markup = InlineKeyboardMarkup(alert_button)


def new_cases_alert(context: CallbackContext) -> None:
    """
    This function periodically(every minute) obtains the breaking coronavirus news url. If the link is new, it
    sends the link to the users who have opted in to receive this.
    """

    if 'latest_breaking_url' not in context.bot_data:
        context.bot_data['latest_breaking_url'] = None

    breaking_url = GulfNews().breaking()

    if breaking_url is not None:
        if breaking_url != context.bot_data['latest_breaking_url']:  # New coronavirus cases/deaths, etc

            ids_query = f"SELECT CHAT_ID, CHAT_NAME FROM CHAT_SETTINGS WHERE ALERTS='✅';"
            ids = connection(ids_query, fetchall=True)

            for chat_id, chat_name in ids:
                context.bot.send_message(chat_id=chat_id, text=f"UPDATE:\n\n{breaking_url}")
                logging.info(f"\nThe breaking news was just sent to: {chat_name}.\n\n")

            context.bot_data['latest_breaking_url'] = breaking_url  # Save the latest breaking news url
            context.dispatcher.persistence.flush()  # Gotta do this to force save sigh


def opt_in_out(update: Update, context: CallbackContext) -> None:
    """This function allows the user to opt in or out of receiving breaking coronavirus news."""

    chat_id = update.effective_chat.id

    query = f'SELECT ALERTS FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};'
    status = connection(query, update=update)  # Connect to db to get current settings

    context.bot.send_message(chat_id=chat_id, text=text.replace('()', status), reply_markup=markup)
    logging.info(f"\n{update.effective_user.first_name} just used /alerts in {get_chat_name(update)}.\n\n")


def update_alert(update: Update, context: CallbackContext) -> None:
    """This function changes the state of /alerts. The state is saved in a database."""

    chat_id = update.effective_chat.id
    call_id = update.callback_query.id

    query = f'SELECT ALERTS FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};'
    update_query = f"UPDATE CHAT_SETTINGS SET ALERTS='()' WHERE CHAT_ID={chat_id};"
    status = connection(query, update=update)

    if status == "❌":
        new_status = '✅'
    else:
        new_status = '❌'

    connection(update_query.replace('()', new_status), table_update=True)
    update_text = text.replace('()', f'{new_status}\n\nYour settings were successfully updated.')

    update.callback_query.edit_message_text(text=update_text, reply_markup=markup)  # Update message to show change
    context.bot.answer_callback_query(callback_query_id=call_id)  # Answer the callback query in clients
    logging.info(f"\n{update.effective_user.first_name} just toggled /alerts in {get_chat_name(update)} to "
                 f"{new_status}.\n\n")
