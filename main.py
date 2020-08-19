import logging
import sys
import pickle
import pprint
import subprocess

import requests
from requests.exceptions import ReadTimeout
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
    if msg == "/graphs" or msg == "/graphs@uaecoronabot":
        context.bot.send_message(chat_id=update.effective_chat.id, text="There is already a /graphs instance in use!",
                                 reply_to_message_id=update.effective_message.message_id)

        logging.info(f"{update.effective_user.name} used /graphs before timeout.\n\n")
        return

    elif msg == "/cancel":
        context.bot.send_message(chat_id=update.effective_chat.id, text="There is... nothing to cancel.",
                                 reply_to_message_id=update.effective_message.message_id)
        logging.info(f"{update.effective_user.name} used /cancel for no reason.\n\n")
        return

    logging.info(f"{update.effective_user.name} said {msg}.")


def off_poll(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id == 476269395:
        updater.stop()
        context.bot.send_message(chat_id=476269395, text='stopped.')


def alert_ppl(context: CallbackContext) -> None:
    # ids = context.dispatcher.user_data.keys()
    # print(ids)
    context.bot.send_message(chat_id=764886971,
                             text="We all come from @BotFather. He is supreme. He will help us triumph against you.")
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
    #         logging.info(f"\nAlert sent to: {_id=}, Title: {user.title}, Username:{user.username}, "
    #                      f"Name: {user.first_name}\n\n")
    #
    #     except Exception as e:
    #         print(f"Exception for {_id}: {e}.")


def enable_proxy(recheck: bool = False) -> None:
    """
    Enable proxy by running a Linux command to setup a localhost TOR proxy server.

    Args:
        recheck (bool): If `True`, check proxy is working properly by calling check_connection(). Default: `False`.
    """
    global proxy

    logging.warning("\nATTEMPTING TO USE PROXY\n")

    subprocess.Popen(['echo', f"'{sudo_pass}'", '|', 'sudo', '-S', 'systemctl', 'status', 'tor'])
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
            logging.critical("\n\n\nFAILED TO CONNECT VIA PROXY, CHECK YOUR INTERNET CONNECTION!\n")
            raise SystemExit
        else:
            logging.warning("\nFAILED TO ESTABLISH CONNECTION.\n\n")
            enable_proxy(recheck=True)

    except Exception as e:
        logging.warning(f"\n\nANOTHER EXCEPTION OCCURRED WHILE CONNECTING: {e}\n")

    else:
        if proxy_on or sys.argv[1] in ('--proxy', '-p'):
            logging.warning("\nRUNNING VIA TOR/SOCKS5 PROXY!\n\n")


if __name__ == "__main__":
    with open('files/token.txt') as f:
        token, sudo_pass = f.read().split(',')

    proxy = {'ptb': None, 'owid': None}

    if len(sys.argv) > 1:
        if sys.argv[1] in ('--proxy', '-p'):
            enable_proxy()

    # Check if connection is working, if not, use proxy-
    check_connection()

    pp = PicklePersistence(filename="files/user_data")
    updater = Updater(token=token, use_context=True, persistence=pp,
                      request_kwargs=proxy['ptb'])
    dp = updater.dispatcher

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

    updater.start_polling()
    updater.idle()
