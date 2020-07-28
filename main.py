import logging
import pickle
import pprint

from telegram import Update
from telegram.ext import (Updater, CommandHandler, PicklePersistence, CallbackQueryHandler, CallbackContext,
                          MessageHandler, Filters, ConversationHandler)

import graphing.ui.utility
from bot_funcs.commands import start, world, uae, helper, ask_feedback, receive_feedback, cancel
from bot_funcs.alert import new_cases_alert, opt_in_out, update_alert
from graphing.ui import datas, entry, navigation, country_maker, trends_ui
from graphing import load_data

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def data_view() -> None:
    with open('files/user_data', 'rb') as f1:
        pprint.PrettyPrinter(indent=2).pprint(pickle.load(f1))


def msgs(update: Update, context: CallbackContext):
    msg = update.message.text
    if msg == "/graphs":
        context.bot.send_message(chat_id=update.effective_chat.id, text="There is already a /graphs instance in use!",
                                 reply_to_message_id=update.effective_message.message_id)

        logging.info(f"{update.effective_user.full_name} used /graphs before timeout.\n\n")
        return

    logging.info(f"{update.effective_user.full_name} said {msg}.")


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
    with open('files/token.txt') as f:
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

    # For toggling alerts-
    dp.add_handler(CallbackQueryHandler(callback=update_alert, pattern="toggle"))

    # For graphs-
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler(command="graphs", callback=entry.call_graph_command)], states={
            datas.MAIN_SELECTOR: [CallbackQueryHandler(callback=entry.show_graph_buttons, pattern="OWID_WRL"),
                                  CallbackQueryHandler(callback=country_maker.make_country_list, pattern="country")],

            datas.COUNTRY_SELECTOR: [CallbackQueryHandler(callback=navigation.go_back_to_main, pattern="back_main"),
                                     CallbackQueryHandler(callback=navigation.previous_page, pattern="previous_page"),
                                     CallbackQueryHandler(callback=navigation.next_page, pattern="next_page"),
                                     CallbackQueryHandler(callback=entry.show_graph_buttons,
                                                          pattern="|".join(datas.iso_codes))],

            datas.TREND_SELECTOR: [CallbackQueryHandler(callback=navigation.go_back_to_main, pattern="back_main"),
                                   CallbackQueryHandler(callback=navigation.go_back_to_countries,
                                                        pattern="back_countries"),
                                   CallbackQueryHandler(callback=navigation.go_back_to_countries,
                                                        pattern="back_countries"),
                                   CallbackQueryHandler(callback=trends_ui.chosen_trend,
                                                        pattern="total_cases|new_cases|total_deaths|new_deaths")],

            datas.GRAPH_OPTIONS: [CallbackQueryHandler(callback=navigation.go_back_to_graph_buttons,
                                                       pattern="back_trends"),
                                  CallbackQueryHandler(callback=trends_ui.toggle_log, pattern="log")],

            ConversationHandler.TIMEOUT: [MessageHandler(callback=graphing.ui.utility.remove_user_data,
                                                         filters=Filters.all)]

        }, fallbacks=[CommandHandler(command='cancel', callback=cancel)], conversation_timeout=120))  # 2 min timeout

    # Random text to bot-
    dp.add_handler(MessageHandler(filters=Filters.text, callback=msgs))

    updater.job_queue.run_repeating(callback=new_cases_alert, interval=90, first=1)  # Run every 90 seconds
    updater.job_queue.run_repeating(callback=graphing.ui.utility.remove_all_user_data, interval=86400, first=2)
    updater.job_queue.run_repeating(callback=load_data.download_file, interval=3600, first=3)  # Run every hour

    data_view()

    updater.start_polling()
    updater.idle()
