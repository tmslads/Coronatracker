# Functions to obtain chatname-
from telegram import Update


def get_chat_name(update: Update) -> str:
    """Helper function to get name of private/group chat."""

    name = update.effective_chat.title
    if name is None:
        name = update.effective_chat.first_name
    return name
