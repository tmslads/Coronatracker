import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .datas import entry_msg, entry_buttons, graph_buttons, selection_msg, MAIN_SELECTOR, TREND_SELECTOR, user_selection


def call_graph_command(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text=entry_msg,
                             reply_markup=InlineKeyboardMarkup(entry_buttons))
    logging.info(msg="In graph command")

    return MAIN_SELECTOR


def show_graph_buttons(update: Update, _: CallbackContext) -> None:
    button_clicked = None

    for button_list in update.callback_query.message.reply_markup.inline_keyboard:
        for button in button_list:

            if button.callback_data == update.callback_query.data:
                if button.text == "The World":
                    # print('here')
                    graph_buttons[0][0].callback_data = "back_main"
                    user_selection['country'] = 'OWID_WRL'
                else:
                    # print("else cond")
                    graph_buttons[0][0].callback_data = "back_countries"
                    user_selection['country'] = update.callback_query.data

                button_clicked = button.text

    # print(graph_buttons)
    updated_selection = selection_msg.replace('()', f"{button_clicked}")
    update.callback_query.edit_message_text(text=updated_selection, parse_mode="MarkdownV2",
                                            reply_markup=InlineKeyboardMarkup(graph_buttons))
    return TREND_SELECTOR
