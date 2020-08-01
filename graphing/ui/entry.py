import logging

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .datas import entry_msg, entry_buttons, graph_buttons, selection_msg, MAIN_SELECTOR, TREND_SELECTOR, user_selection
from helpers.namer import get_chat_name


def call_graph_command(update: Update, context: CallbackContext) -> MAIN_SELECTOR:
    """Displays the main selection screen when user first uses /graphs."""
    context.bot.send_message(chat_id=update.effective_chat.id, text=entry_msg,
                             reply_markup=InlineKeyboardMarkup(entry_buttons))
    logging.info(msg=f"\n{update.effective_user.name} is using /graphs in {get_chat_name(update)}")

    return MAIN_SELECTOR


def show_trend_buttons(update: Update, _: CallbackContext) -> None:
    """Displays the trend buttons and changes the callback data of the back button so back button works as expected."""
    button_clicked = None

    for button_list in update.callback_query.message.reply_markup.inline_keyboard:
        for button in button_list:
            if button.callback_data == update.callback_query.data:
                if button.text == "The World 🌎":  # Change to this, so clicking it will return user to main screen.
                    graph_buttons[0][0].callback_data = "back_main"
                    user_selection['country'] = 'OWID_WRL'
                else:  # Change to this, so clicking it will return user to country select screen.
                    graph_buttons[0][0].callback_data = "back_countries"
                    user_selection['country'] = update.callback_query.data

                button_clicked = button.text

    updated_selection = selection_msg.replace('()', f"{button_clicked}")
    logging.info(f"{update.callback_query.from_user.name} has selected {button_clicked}.")

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=updated_selection, parse_mode="MarkdownV2",
                                            reply_markup=InlineKeyboardMarkup(graph_buttons))
    return TREND_SELECTOR
