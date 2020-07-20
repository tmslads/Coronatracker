import logging
import pickle
import pprint

from telegram.ext import (Updater, CommandHandler, PicklePersistence, CallbackQueryHandler, CallbackContext,
                          MessageHandler, Filters, ConversationHandler)

from bot_funcs.commands import start, world, uae, helper, ask_feedback, receive_feedback, cancel
from bot_funcs.alert import new_cases_alert, opt_in_out, update_alert

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def data_view() -> None:
    with open('files/user_data', 'rb') as f1:
        pprint.PrettyPrinter(indent=2).pprint(pickle.load(f1))


def msgs(update, _):
    print(f"{update.effective_user.full_name} said {update.message.text}")


def alert_ppl(context: CallbackContext) -> None:
    ids = []
    for _id in ids:
        try:
            context.bot.send_message(chat_id=_id,
                                     text="NEW FEATURE:\n\nYou can now choose to receive breaking coronavirus news for "
                                          "the UAE! \n\nThis will include new cases, deaths, recoveries, etc. The bot "
                                          "will send you a message whenever there is such news "
                                          "(usually once a day).\n\n"
                                          "Click /alerts to get started.\n"
                                          "Or, click /help to know various other bot functions.\n\n"
                                          "This bot is actively maintained and more features such as graphs are coming "
                                          "soon!")
            logging.info(f"\nAlert sent to: {_id}\n\n")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    with open('files/token.txt', 'r') as f:
        token = f.read()

    pp = PicklePersistence(filename="files/user_data")
    updater = Updater(token=token, use_context=True, persistence=pp)
    dp = updater.dispatcher

    for k, v in {'start': start, 'help': helper, 'world': world, 'uae': uae}.items():
        dp.add_handler(CommandHandler(command=k, callback=v))

    dp.add_handler(CommandHandler(command='alerts', callback=opt_in_out))

    # For feedback-
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(command='feedback', callback=ask_feedback)],
        states={1: [MessageHandler(filters=Filters.text & ~ Filters.command, callback=receive_feedback)]},
        fallbacks=[CommandHandler(command='cancel', callback=cancel)]))

    # Random text to bot-
    dp.add_handler(MessageHandler(filters=Filters.text, callback=msgs))

    # For toggling alerts-
    dp.add_handler(CallbackQueryHandler(callback=update_alert, pattern="toggle"))

    updater.job_queue.run_repeating(callback=new_cases_alert, interval=90, first=1)

    data_view()

    updater.start_polling()
    updater.idle()
