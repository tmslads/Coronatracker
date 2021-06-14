import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .datas import COUNTRY_SELECTOR, country_msg
from .utility import generate_country_list


def make_country_list(update: Update, context: CallbackContext) -> COUNTRY_SELECTOR:
    """Fetches the country page and modifies it in-place to include main menu and previous/next page buttons."""
    if 'current_page' not in context.user_data:
        context.user_data['current_page'] = 1
    if 'country_list' not in context.user_data:
        context.user_data['country_list'] = generate_country_list()

    page = context.user_data['current_page']
    country_list = context.user_data['country_list']

    country_page = country_list[page - 1].copy()  # Make deep copy of list to prevent errors. '-1' for indexing purposes

    logging.info(msg=f"{update.callback_query.from_user.name} is on page {page}.")

    country_page.insert(0, [InlineKeyboardButton(text="< Previous Page", callback_data="previous_page"),
                            InlineKeyboardButton(text="Next Page >", callback_data="next_page")])

    country_page.insert(0, [InlineKeyboardButton(text="<< Main menu", callback_data="back_main")])

    update.callback_query.answer()
    msg = update.callback_query.edit_message_text(text=country_msg.replace('()', str(page)), parse_mode="MarkdownV2",
                                                  reply_markup=InlineKeyboardMarkup(country_page))
    context.user_data['graph_id'] = msg.message_id
    return COUNTRY_SELECTOR
