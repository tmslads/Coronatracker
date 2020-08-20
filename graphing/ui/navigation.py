# Navigation for countries and for going back to 'main' screen

import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from helpers.msg_deletor import del_msg
from .country_maker import make_country_list
from .datas import (entry_msg, entry_buttons, MAIN_SELECTOR, graph_buttons, selection_msg, TREND_SELECTOR,
                    user_selection, iso_codes, COUNTRY_SELECTOR, trend_buttons)


def go_back_to_main(update: Update, _: CallbackContext) -> MAIN_SELECTOR:
    """Navigates the user back to the main selector."""
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=entry_msg, reply_markup=InlineKeyboardMarkup(entry_buttons))
    logging.info(msg=f"{update.callback_query.from_user.name} went back to the main menu.")

    return MAIN_SELECTOR


def go_back_to_countries(update: Update, context: CallbackContext) -> None:
    """Navigates the user back to the country selector."""
    logging.info(msg=f"{update.callback_query.from_user.name} went back to the country list.")

    return make_country_list(update, context)


def go_back_to_trend_buttons(update: Update, context: CallbackContext) -> None:
    """Navigates the user back to trend buttons."""
    if user_selection['country'] == "OWID_WRL":
        msg = selection_msg.replace("()", "The World")
    else:
        msg = selection_msg.replace("()", f"{iso_codes[user_selection['country']]}")

    update.callback_query.answer()
    del_msg(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg,
                             reply_markup=InlineKeyboardMarkup(graph_buttons), parse_mode="MarkdownV2")

    context.user_data['log'] = False  # Reset log to False if user left from log=True state.
    trend_buttons[0][-1].text = "Log scale ❌"
    logging.info(f"{update.callback_query.from_user.name} is now back in trend buttons.")

    return TREND_SELECTOR


def next_page(update: Update, context: CallbackContext) -> COUNTRY_SELECTOR:
    """Navigates the user to the next page in the country list."""
    context.user_data['current_page'] += 1

    if context.user_data['current_page'] > 9:
        context.user_data['current_page'] = 9
        update.callback_query.answer()
        return COUNTRY_SELECTOR

    make_country_list(update, context)

    return COUNTRY_SELECTOR


def previous_page(update: Update, context: CallbackContext) -> COUNTRY_SELECTOR:
    """Navigates the user to the previous page in the country list."""
    context.user_data['current_page'] -= 1

    if context.user_data['current_page'] < 1:
        context.user_data['current_page'] = 1
        update.callback_query.answer()
        return COUNTRY_SELECTOR

    make_country_list(update, context)

    return COUNTRY_SELECTOR
