import logging
from datetime import datetime

from telegram import Update, ForceReply, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from helpers.namer import get_chat_name
from scrapers.worldometer import WorldMeter
from graphing.ui.datas import remove_all_user_data

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def helper(update: Update, context: CallbackContext) -> None:
    msg = "This bot gives you up to date information about the coronavirus in the UAE\. Here are the commands" \
          " supported:\n\n" \
          "1\. /world \- Sends you the total number of coronavirus cases, recoveries and deaths globally\.\n" \
          "2\. /uae \- Sends you the latest coronavirus information for the UAE\.\n" \
          "3\. /alerts \- Opt in/out to get breaking coronavirus news such as new cases, deaths, etc\. for the UAE " \
          "\(usually once a day\)\." \
          "\n\nData sources:\n" \
          "1\. [Gulfnews](https://gulfnews.com) for alerts\.\n" \
          "2\. [Worldometers](https://www.worldometers.info/coronavirus) for /uae and /world\.\n\n" \
          "You can find the source code of this project [here](https://github.com/tmslads/Coronatracker)\.\n\n" \
          "This bot is actively maintained by: @Hoppingturtles"

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2",
                             disable_web_page_preview=True)
    logging.info(f"\n{update.effective_user.first_name} just used /help in {get_chat_name(update)}.\n\n")


def start(update: Update, context: CallbackContext) -> None:
    msg = "This bot gives you information related to the Novel Coronavirus (SARS-CoV-2) in the UAE. Type /help " \
          "to get a list of commands."

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    logging.info(f"\n{update.effective_user.first_name} just used /start in {get_chat_name(update)}.\n\n")


def uae(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    init = WorldMeter()
    new, totals = init.ae_data()

    msg = f"Here's a breakdown of UAE's coronavirus cases:\n\n" \
          f"Total cases: {totals[0]}  {new['new_cases']}\n" \
          f"Total deaths: {totals[1]}  {new['new_deaths']}\n" \
          f"Total recovered: {totals[2]}  {new['new_recoveries']}\n" \
          f"Active cases: {totals[3]}\n" \
          f"Critical cases: {totals[4]}\n" \
          f"Total cases/1M population: {totals[5]}\n" \
          f"Deaths/1M population: {totals[6]}\n" \
          f"Total tests: {totals[7]}\n" \
          f"Tests/1M population: {totals[8]}\n\n" \
          f"There's roughly 1 case in every {totals[10]} people, 1 death in every {totals[11]} " \
          f"people and 1 test done in every {totals[12]} people\.\n\n" \
          f"_Last updated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M:%S')} UTC_"

    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")
    logging.info(f"\n{update.effective_user.first_name} just used /uae in {get_chat_name(update)}.\n\n")


def world(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    init = WorldMeter()
    total, dead, recovered = init.latest_data()
    msg = f"Latest coronavirus stats across the globe:\n\n" \
          f"`☣ Infected: {total}\n" \
          f"☠ Dead: {dead}\n" \
          f"🩹 Recoveries: {recovered}`\n\n" \
          f"_Last updated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M:%S')} UTC_"

    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='MarkdownV2')
    logging.info(f"\n{update.effective_user.first_name} just used /world in {get_chat_name(update)}.\n\n")


def ask_feedback(update: Update, context: CallbackContext) -> int:
    logging.info(msg=f"\n{update.effective_user.full_name} just used /feedback in {get_chat_name(update)}\n\n")

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="What would you like suggest? You can submit a bug report, feature request, "
                                  "anything!\nMake sure to read /help before submitting.\n\nType /cancel to cancel.",
                             reply_markup=ForceReply(selective=True))

    return 1


def receive_feedback(update: Update, context: CallbackContext) -> int:
    with open("../files/feedback.txt", 'a') as f:
        feedback = f"{update.effective_user.full_name} suggested: {update.message.text}\n\n"
        f.write(feedback)

    logging.info(msg=f'\n{feedback}')

    context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for your feedback!")
    return -1


def cancel(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled.",
                             reply_markup=ReplyKeyboardRemove(selective=True))
    logging.info(msg=f"\nThe user cancelled the request.\n\n")

    remove_all_user_data(context)

    return -1
