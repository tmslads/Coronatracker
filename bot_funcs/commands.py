import logging
from datetime import datetime, timezone

from telegram import Update, ForceReply, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from helpers.namer import get_chat_name
from helpers.msg_deletor import del_msg
from scrapers.worldometer import WorldMeter
from graphing.ui.utility import remove_all_user_data

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def helper(update: Update, context: CallbackContext) -> None:
    """Sends a help message to the user explaining available bot commands."""
    msg = "This bot gives you up to date information about the coronavirus\. Here are the commands" \
          " supported:\n\n" \
          "1\. /world \- Sends you the total number of coronavirus cases, recoveries and deaths globally\.\n" \
          "2\. /uae \- Sends you the latest coronavirus information for the UAE\.\n" \
          "3\. /alerts \- Opt in/out to get breaking coronavirus news such as new cases, deaths, etc\. for the UAE " \
          "\(usually once a day\)\.\n" \
          "4\. /graphs \- View detailed coronavirus graphs globally or for any country\. You can choose from 7 " \
          "different trends\." \
          "\n\nData sources:\n" \
          "1\. [Gulfnews](https://gulfnews.com) for alerts\.\n" \
          "2\. [Worldometers](https://www.worldometers.info/coronavirus) for /uae and /world\.\n" \
          "3\. [OurWorldInData](https://github.com/owid/covid-19-data/tree/master/public/data) for /graphs\.\n\n" \
          "You can find the source code of this project [here](https://github.com/tmslads/Coronatracker)\.\n\n" \
          "This bot is actively maintained by: @Hoppingturtles"

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="MarkdownV2",
                             disable_web_page_preview=True)
    logging.info(f"\n{update.effective_user.first_name} just used /help in {get_chat_name(update)}.\n\n")


def start(update: Update, context: CallbackContext) -> None:
    """Starts the bot for the user for the first time."""
    msg = "This bot gives you information related to the Novel Coronavirus (SARS-CoV-2) and the Coronavirus Disease " \
          "(COVID-19).\n\n Type /help " \
          "to get a list of commands."

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    logging.info(f"\n{update.effective_user.first_name} just used /start in {get_chat_name(update)}.\n\n")


def uae(update: Update, context: CallbackContext) -> None:
    """Sends the user detailed coronavirus statistics, for the UAE."""
    chat_id = update.effective_chat.id

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    init = WorldMeter()
    new, totals = init.ae_data()

    msg = f"Here's a breakdown of UAE's coronavirus cases:\n\n" \
          f"Total cases: {totals[0]}  {new['new_cases']}\n" \
          f"Total deaths: {totals[1]}  {new['new_deaths']}\n" \
          f"Total recovered: {totals[2]}  {new['new_recoveries']}\n" \
          f"Active cases: {totals[3]}\n" \
          f"Critical cases: {new['critical']}\n" \
          f"Total cases/1M population: {totals[4]}\n" \
          f"Deaths/1M population: {totals[5]}\n" \
          f"Total tests: {totals[6]}\n" \
          f"Tests/1M population: {totals[7]}\n\n" \
          f"There's roughly 1 case in every {totals[9]} people, 1 death in every {totals[10]} " \
          f"people and 1 test done in every {totals[11]} people\.\n\n" \
          f"_Last updated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M:%S')} UTC_"

    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="MarkdownV2")
    logging.info(f"\n{update.effective_user.first_name} just used /uae in {get_chat_name(update)}.\n\n")


def world(update: Update, context: CallbackContext) -> None:
    """Sends the user worldwide coronavirus statistics."""
    chat_id = update.effective_chat.id

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    init = WorldMeter()
    total, dead, recovered = init.latest_data()
    msg = f"Latest coronavirus stats across the globe:\n\n" \
          f"`☣ Infected: {total}\n" \
          f"☠ Dead: {dead}\n" \
          f"🩹 Recoveries: {recovered}`\n\n" \
          f"_Last updated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M:%S')} UTC_"

    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='MarkdownV2')
    logging.info(f"\n{update.effective_user.first_name} just used /world in {get_chat_name(update)}.\n\n")


def ask_feedback(update: Update, context: CallbackContext) -> int:
    """Sends a message to the user asking for feedback. Called when user clicks /feedback."""
    logging.info(msg=f"\n{update.effective_user.name} just used /feedback in {get_chat_name(update)}\n\n")

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="What would you like suggest? You can submit a bug report, feature request, "
                                  "anything!\nMake sure to read /help before submitting.\n\nType /cancel to cancel.",
                             reply_markup=ForceReply(selective=True))

    return 1


def receive_feedback(update: Update, context: CallbackContext) -> int:
    """Get feedback from user, display in console and save to file."""
    with open("files/feedback.txt", 'a') as f:
        feedback = f"{update.effective_user.name} suggested: {update.message.text}\n\n"
        f.write(feedback)

    logging.info(msg=f'\n{feedback}')

    context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you for your feedback!")
    return -1


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels the current operation."""
    try:
        del_msg(update, context, msg_no=1)
    except Exception as e:
        print(e)

    context.bot.send_message(chat_id=update.effective_chat.id, text="The command was cancelled.",
                             reply_markup=ReplyKeyboardRemove(selective=True))
    logging.info(msg=f"\nThe user cancelled the request.\n\n")

    remove_all_user_data(context)

    return -1
