from telegram import Update
from telegram.ext import CallbackContext


def del_msg(update: Update, context: CallbackContext) -> None:
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
