import html
import json
import logging
import os
import pickle
import pprint
import threading
import time
import traceback

from telegram import Update, ParseMode
from telegram.ext import (Updater, CommandHandler, PicklePersistence,
                          CallbackQueryHandler, CallbackContext,
                          MessageHandler, Filters, ConversationHandler,
                          ChatMemberHandler)
from flask import Flask

import graphing.ui.utility
from bot_funcs.commands import start, world, uae, helper, ask_feedback, receive_feedback, cancel, vaccine
from bot_funcs.alert import new_cases_alert, opt_in_out, update_alert
from bot_funcs.blocked import user_blocked
from graphing.ui import datas, entry, navigation, country_maker, trends_ui
from graphing import load_data

app = Flask(__name__)

logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fh = logging.FileHandler('files/logs.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

start_time = time.time()


@app.route('/')
def deploy_info() -> str:
    return f"I'm https://t.me/uaecoronabot and I'm deployed on repl.it. I've been up for: {time.time() - start_time} " \
           f"seconds."


def data_view() -> None:
    with open('files/user_data', 'rb') as f1:
        pprint.PrettyPrinter(indent=2).pprint(pickle.load(f1))


def msgs(update: Update, _: CallbackContext):
    msg = update.message.text
    if msg == "/graphs" or msg == "/graphs@uaecoronabot":
        update.message.reply_text(
            text=
            "There is already a /graphs instance in use!\n\nUse /cancel to cancel.",
        )

        logger.info(
            f"{update.effective_user.name} used /graphs before timeout.\n\n")
        return

    elif msg == "/cancel":
        update.message.reply_text(text="There is... nothing to cancel.")
        logger.info(f"{update.effective_user.name} said {msg}.")


def off_poll(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 476269395:
        context.bot.send_message(chat_id=476269395, text='stopping...')
        updater.stop()


def errors(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error,
                                         context.error.__traceback__)
    tb_string = ''.join(tb_list)

    update_str = update.to_dict() if isinstance(update,
                                                Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>')
    if isinstance(update, Update) and update.effective_message:
        if len(message) > 4096:
            message = message[-4095:]
        update.effective_message.reply_text(
            'An error occurred. The error has been forwarded to the bot developer '
            '(@Hoppingturtles)')
    # Finally, send the message
    context.bot.send_message(chat_id=476269395,
                             text=message,
                             parse_mode=ParseMode.HTML)


# def alert_ppl(context: CallbackContext) -> None:
# ids = context.dispatcher.chat_data.keys()
# print(ids)
# context.bot.send_message(chat_id=764886971,
#                          text="no")
# print('sent')

# for _id in ids:
#     if _id > 0:
#         continue
#     try:
#         user = context.bot.get_chat(chat_id=_id)
#         context.bot.send_message(chat_id=_id,
#                                  text=vaccine_msg,
#                                  parse_mode="MarkdownV2")
#         logger.info(f"\nAlert sent to: {_id=}, Title: {user.title}, Username:{user.username}, "
#                     f"Name: {user.first_name}\n\n")
#
#     except Exception as e:
#         print(f"Exception for {_id}: {e}.")

pp = PicklePersistence(filename="files/user_data")
updater = Updater(token=os.environ['token'], persistence=pp)
dp = updater.dispatcher

for k, v in {
        'start': start,
        'help': helper,
        'world': world,
        'uae': uae,
        'stop': off_poll,
        'vaccine': vaccine
}.items():
    dp.add_handler(CommandHandler(command=k, callback=v))

dp.add_handler(CommandHandler(command='alerts', callback=opt_in_out))

# For feedback-
dp.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler(command='feedback', callback=ask_feedback)
        ],
        states={
            1: [
                MessageHandler(filters=Filters.text & ~Filters.command,
                               callback=receive_feedback)
            ]
        },
        fallbacks=[CommandHandler(command='cancel', callback=cancel)]))

# For toggling alerts-
dp.add_handler(CallbackQueryHandler(callback=update_alert, pattern="toggle"))

# For graphs-
dp.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler(command="graphs", callback=entry.call_graph_command)
        ],
        states={
            datas.MAIN_SELECTOR: [
                CallbackQueryHandler(callback=entry.show_trend_buttons,
                                     pattern="OWID_WRL"),
                CallbackQueryHandler(callback=country_maker.make_country_list,
                                     pattern="country")
            ],
            datas.COUNTRY_SELECTOR: [
                CallbackQueryHandler(callback=navigation.go_back_to_main,
                                     pattern="back_main"),
                CallbackQueryHandler(callback=navigation.previous_page,
                                     pattern="previous_page"),
                CallbackQueryHandler(callback=navigation.next_page,
                                     pattern="next_page"),
                CallbackQueryHandler(callback=entry.show_trend_buttons,
                                     pattern="|".join(datas.iso_codes))
            ],
            datas.TREND_SELECTOR: [
                CallbackQueryHandler(callback=navigation.go_back_to_main,
                                     pattern="back_main"),
                CallbackQueryHandler(callback=navigation.go_back_to_countries,
                                     pattern="back_countries"),
                CallbackQueryHandler(
                    callback=trends_ui.chosen_trend,
                    pattern="total_cases|new_cases|total_deaths|new_deaths|"
                    "total_tests|new_tests|positivity_rate")
            ],
            datas.GRAPH_OPTIONS: [
                CallbackQueryHandler(
                    callback=navigation.go_back_to_trend_buttons,
                    pattern="back_trends"),
                CallbackQueryHandler(callback=trends_ui.toggle_log,
                                     pattern="log")
            ],
            ConversationHandler.TIMEOUT: [
                MessageHandler(callback=graphing.ui.utility.remove_user_data,
                               filters=Filters.all),
                CallbackQueryHandler(
                    callback=graphing.ui.utility.remove_user_data)
            ]
        },
        fallbacks=[CommandHandler(command='cancel', callback=cancel)],
        conversation_timeout=300))  # 5 min timeout

# Random text to bot-
dp.add_handler(
    MessageHandler(filters=Filters.text & Filters.chat_type.private,
                   callback=msgs))
dp.add_handler(ChatMemberHandler(user_blocked))
dp.add_error_handler(errors)

updater.job_queue.run_repeating(callback=new_cases_alert, interval=90,
                                first=1)  # Run every 90 seconds
updater.job_queue.run_repeating(
    callback=graphing.ui.utility.remove_all_user_data, interval=86400, first=2)
updater.job_queue.run_repeating(callback=load_data.download_file,
                                interval=3600,
                                first=3)

updater.start_polling(timeout=15, read_latency=5.0)

threading.Thread(
    target=lambda: app.run(host='0.0.0.0')).start()  # For deployment on replit

updater.idle()
