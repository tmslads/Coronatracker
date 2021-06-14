import logging

from telegram import Update
from telegram.ext import CallbackContext


def del_msg(update: Update, context: CallbackContext, msg_no: int = 0) -> bool:
    """Delete the message sent by the bot."""
    try:
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=update.effective_message.message_id + msg_no)
    except Exception as e:
        logging.info(msg=f"\nMessage couldn't be deleted due to: {e}.")
        return False
    return True
