# Navigation for countries and for going back to 'main' screen

import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from helpers.msg_deletor import del_msg
from .country_maker import make_country_list
from .datas import (entry_msg, entry_buttons, MAIN_SELECTOR, graph_buttons, selection_msg, TREND_SELECTOR,
                    user_selection, iso_codes, COUNTRY_SELECTOR)


def go_back_to_main(update: Update, _: CallbackContext) -> MAIN_SELECTOR:
    update.callback_query.edit_message_text(text=entry_msg, reply_markup=InlineKeyboardMarkup(entry_buttons))
    logging.info(msg=f"Inside go_back_to_main func")
    return MAIN_SELECTOR


def go_back_to_countries(update: Update, context: CallbackContext) -> None:
    return make_country_list(update, context)


def go_back_to_graph_buttons(update: Update, context: CallbackContext) -> None:
    if user_selection['country'] == "OWID_WRL":
        msg = selection_msg.replace("()", "The World")
    else:
        msg = selection_msg.replace("()", f"{iso_codes[user_selection['country']]}")

    del_msg(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                             reply_markup=InlineKeyboardMarkup(graph_buttons), parse_mode="MarkdownV2")

    context.user_data['log'] = False  # Reset log to False if user left from log=True state.

    return TREND_SELECTOR


def next_page(update: Update, context: CallbackContext) -> COUNTRY_SELECTOR:
    context.user_data['current_page'] += 1
    make_country_list(update, context)

    return COUNTRY_SELECTOR


def previous_page(update: Update, context: CallbackContext) -> COUNTRY_SELECTOR:
    context.user_data['current_page'] -= 1
    make_country_list(update, context)

    return COUNTRY_SELECTOR
