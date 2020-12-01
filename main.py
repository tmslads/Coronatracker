import logging
import sys
import pickle
import pprint
import subprocess
from socket import timeout
from os import environ

import requests
from requests.exceptions import ReadTimeout
from telegram import Update
from telegram.ext import (Updater, CommandHandler, PicklePersistence, CallbackQueryHandler, CallbackContext,
                          MessageHandler, Filters, ConversationHandler)
from telegram.vendor.ptb_urllib3.urllib3.contrib.socks import ConnectTimeoutError

import graphing.ui.utility
from bot_funcs.commands import start, world, uae, helper, ask_feedback, receive_feedback, cancel
from bot_funcs.alert import new_cases_alert, opt_in_out, update_alert
from graphing.ui import datas, entry, navigation, country_maker, trends_ui
from graphing import load_data

logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fh = logging.FileHandler('files/logs.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d - %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def data_view() -> None:
    with open('files/user_data', 'rb') as f1:
        pprint.PrettyPrinter(indent=2).pprint(pickle.load(f1))


def msgs(update: Update, context: CallbackContext):
    msg = update.message.text
    if msg == "/graphs" or msg == "/graphs@uaecoronabot":
        context.bot.send_message(chat_id=update.effective_chat.id, text="There is already a /graphs instance in use!"
                                                                        "\n\nUse /cancel to cancel.",
                                 reply_to_message_id=update.effective_message.message_id)

        logger.info(f"{update.effective_user.name} used /graphs before timeout.\n\n")
        return

    elif msg == "/cancel":
        context.bot.send_message(chat_id=update.effective_chat.id, text="There is... nothing to cancel.",
                                 reply_to_message_id=update.effective_message.message_id)
        logger.info(f"{update.effective_user.name} used /cancel for no reason.\n\n")
        return

    logger.info(f"{update.effective_user.name} said {msg}.")


def off_poll(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 476269395:
        context.bot.send_message(chat_id=476269395, text='stopping...')
        updater.stop()


def alert_ppl(context: CallbackContext) -> None:
    # ids = context.dispatcher.user_data.keys()
    # print(ids)
    context.bot.send_message(chat_id=764886971,
                             text="no")
    print('sent')
    # for _id in ids:
    #     try:
    #         user = context.bot.get_chat(chat_id=_id)
    #         context.bot.send_message(chat_id=_id,
    #                                  text="*NEW FEATURES:*\n\nYou can now finally try out /graphs\! Choose between 7 "
    #                                       "trends, which include cases, deaths, tests, and test positivity rate\.\n\n"
    #                                       "You can now also use /feedback to give any feedback\! It goes directly to "
    #                                       "the bot creator\.",
    #                                  parse_mode="MarkdownV2")
    #         logger.info(f"\nAlert sent to: {_id=}, Title: {user.title}, Username:{user.username}, "
    #                      f"Name: {user.first_name}\n\n")
    #
    #     except Exception as e:
    #         print(f"Exception for {_id}: {e}.")


def disable_proxy(*args) -> None:
    """Disables proxy after receiving a stop signal."""
    if proxy['ptb'] is not None:
        command = f"echo '{sudo_pass}' | sudo -S systemctl stop tor; sudo systemctl disable tor"
        subprocess.call(command, shell=True)
        logger.warning("PROXY STOPPED")
    logger.info("------ STOP ------")


def enable_proxy(recheck: bool = False) -> None:
    """
    Enable proxy by running a Linux command to setup a localhost TOR proxy server.

    Args:
        recheck (bool): If `True`, check proxy is working properly by calling check_connection(). Default: `False`.
    """
    global proxy

    logger.warning("\nATTEMPTING TO USE PROXY\n")
    command = f"echo '{sudo_pass}' | sudo -S systemctl start tor; sudo systemctl enable tor"
    subprocess.call(command, shell=True)

    proxy = {'ptb': {'proxy_url': "socks5://127.0.0.1:9050"}, 'owid': {"https": 'socks5://127.0.0.1:9050'}}

    if recheck:
        check_connection(proxy_on=True)


def check_connection(proxy_on: bool = False):
    """
    Checks if connection to websites is censored by making a request to them. Uses a SOCKS5 proxy via TOR relay
    if request timed out(restricted).

    Args:
        proxy_on (bool): If `True`, proxy is used to connect to website. Default: `False`.
    """
    try:
        requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=12, proxies=proxy['owid'])
        requests.get(f"https://ourworldindata.org", timeout=12, proxies=proxy['owid'])

    except ReadTimeout:
        if proxy_on:
            logger.critical("\n\n\nFAILED TO CONNECT VIA PROXY, CHECK YOUR INTERNET CONNECTION!\n")
            raise SystemExit
        else:
            logger.warning("\nFAILED TO ESTABLISH CONNECTION.\n\n")
            enable_proxy(recheck=True)

    except Exception as e:
        logger.warning(f"\n\nANOTHER EXCEPTION OCCURRED WHILE CONNECTING: {e}\n")

    else:
        if proxy_on or sys.argv[-1] in ('--proxy', '-p'):
            logger.warning("\nRUNNING VIA TOR/SOCKS5 PROXY!\n\n")


with open('files/token.txt') as f:
    token, sudo_pass = f.read().split(',')

proxy = {'ptb': None, 'owid': None}

if len(sys.argv) > 1:
    if sys.argv[1] in ('--proxy', '-p'):
        enable_proxy()

# Check if connection is working, if not, use proxy-
check_connection()

pp = PicklePersistence(filename="files/user_data")
updater = Updater(token=token, persistence=pp, user_sig_handler=disable_proxy,
                  request_kwargs=proxy['ptb'])
dp = updater.dispatcher

# if 'last_log_delete' not in pp.get_bot_data():

for k, v in {'start': start, 'help': helper, 'world': world, 'uae': uae, 'stop': off_poll}.items():
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
    entry_points=[CommandHandler(command="graphs", callback=entry.call_graph_command)],

    states={
        datas.MAIN_SELECTOR: [CallbackQueryHandler(callback=entry.show_trend_buttons, pattern="OWID_WRL"),
                              CallbackQueryHandler(callback=country_maker.make_country_list, pattern="country")],

        datas.COUNTRY_SELECTOR: [CallbackQueryHandler(callback=navigation.go_back_to_main, pattern="back_main"),
                                 CallbackQueryHandler(callback=navigation.previous_page, pattern="previous_page"),
                                 CallbackQueryHandler(callback=navigation.next_page, pattern="next_page"),
                                 CallbackQueryHandler(callback=entry.show_trend_buttons,
                                                      pattern="|".join(datas.iso_codes))],

        datas.TREND_SELECTOR: [CallbackQueryHandler(callback=navigation.go_back_to_main, pattern="back_main"),
                               CallbackQueryHandler(callback=navigation.go_back_to_countries,
                                                    pattern="back_countries"),
                               CallbackQueryHandler(callback=trends_ui.chosen_trend,
                                                    pattern="total_cases|new_cases|total_deaths|new_deaths|"
                                                            "total_tests|new_tests|positivity_rate")],

        datas.GRAPH_OPTIONS: [CallbackQueryHandler(callback=navigation.go_back_to_trend_buttons,
                                                   pattern="back_trends"),
                              CallbackQueryHandler(callback=trends_ui.toggle_log, pattern="log")],

        ConversationHandler.TIMEOUT: [MessageHandler(callback=graphing.ui.utility.remove_user_data,
                                                     filters=Filters.all),
                                      CallbackQueryHandler(callback=graphing.ui.utility.remove_user_data)]

    },
    fallbacks=[CommandHandler(command='cancel', callback=cancel)], conversation_timeout=300))  # 5 min timeout

# Random text to bot-
dp.add_handler(MessageHandler(filters=Filters.text, callback=msgs))

updater.job_queue.run_repeating(callback=new_cases_alert, interval=90, first=1)  # Run every 90 seconds
updater.job_queue.run_repeating(callback=graphing.ui.utility.remove_all_user_data, interval=86400, first=2)
updater.job_queue.run_repeating(callback=load_data.download_file, interval=3600, first=3, context=proxy)
# updater.job_queue.run_repeating(callback=alert_ppl, interval=36000, first=3)  # Run every hour

data_view()

try:
    # updater.start_polling(timeout=15, read_latency=5.0)
    updater.start_webhook(listen="0.0.0.0",  port=int(environ.get('PORT', 8443)), url_path=environ.get('token'))
    updater.bot.setWebhook(f"https://coronatrackerbot.herokuapp.com/{environ.get('token')}")
except (timeout, ConnectTimeoutError):
    pass
updater.idle()
