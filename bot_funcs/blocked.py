# File to handle cases when users have blocked the bot, by deleting them from the database.

import logging

from telegram import Update
from telegram.ext import CallbackContext

from helpers.db_connector import connection


def user_blocked(update: Update, _: CallbackContext) -> None:
    logging.info(f'\nThe user {update.effective_user.name} has blocked the bot, removing from database...\n\n')
    connection(query=f'DELETE FROM CHAT_SETTINGS WHERE CHAT_ID={update.effective_chat.id};', table_update=True)
    logging.info(f'\nThe user was removed from database.')
