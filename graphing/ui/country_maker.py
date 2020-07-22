import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .datas import COUNTRY_SELECTOR, generate_country_list, country_msg


def make_country_list(update: Update, context: CallbackContext) -> COUNTRY_SELECTOR:
    logging.info(msg=f"\nIn make_country_list func.\n\n")
    # context.bot.answer_callback_query(callback_query_id=update.callback_query.id, text="Under development!",
    #                                   show_alert=True)

    if 'current_page' not in context.user_data:
        context.user_data['current_page'] = 1
    if 'country_list' not in context.user_data:
        context.user_data['country_list'] = generate_country_list()

    page = context.user_data['current_page']
    country_list = context.user_data['country_list']

    country_page = country_list[page - 1].copy()  # Make deep copy of list to avoid potential errors

    logging.info(msg=f"On page {page}")
    if page == 1:
        country_page.insert(0, [InlineKeyboardButton(text="Next Page >", callback_data="next_page")])
    elif 1 < page < 6:
        country_page.insert(0, [InlineKeyboardButton(text="< Previous Page", callback_data="previous_page"),
                                InlineKeyboardButton(text="Next Page >", callback_data="next_page")])

    else:
        country_page.insert(0, [InlineKeyboardButton(text="< Previous Page", callback_data="previous_page")])

    country_page.insert(0, [InlineKeyboardButton(text="<< Main menu", callback_data="back_main")])

    update.callback_query.edit_message_text(text=country_msg.replace('()', str(page)), parse_mode="MarkdownV2",
                                            reply_markup=InlineKeyboardMarkup(country_page))

    return COUNTRY_SELECTOR
