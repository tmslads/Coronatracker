from telegram import Update
from telegram.ext import CallbackContext
from scrapers.worldometer import WorldMeter


def helper(update: Update, context: CallbackContext) -> None:
    msg = "This bot gives you up to date information about the coronavirus in the UAE. Here are the commands" \
          " supported:\n\n" \
          "1. /world - Gives total number of coronavirus cases, recoveries and deaths globally.\n" \
          "2. /UAE - Gives UAE related coronavirus information."

    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def start(update: Update, context: CallbackContext) -> None:
    msg = "This bot gives you information related to the Novel Coronavirus (SARS-CoV-2) in the UAE. Type /help " \
          "to get a list of commands."
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def uae(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    init = WorldMeter()
    new, totals = init.ae_data()

    msg = "Here is a breakdown of UAE coronavirus cases:\n\n" \
          f"Total cases: {totals[0]}  {new['new_cases'].replace('+', '🔺')}\n" \
          f"Total deaths: {totals[1]}  {new['new_deaths'].replace('+', '🔺')}\n" \
          f"Total recovered: {totals[2]}\n" \
          f"Active cases: {totals[3]}\n" \
          f"Critical cases: {totals[4]}\n" \
          f"Total cases/1M population: {totals[5]}\n" \
          f"Deaths/1M population: {totals[6]}\n" \
          f"Total tests: {totals[7]}\n" \
          f"Tests/1M population: {totals[8]}"

    context.bot.send_message(chat_id=chat_id, text=msg)


def world(update: Update, context: CallbackContext) -> None:

    chat_id = update.effective_chat.id

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    init = WorldMeter()
    total, dead, recovered = init.latest_data()
    msg = f"Latest coronavirus stats across the globe:\n\n" \
          f"`☣ Infected: {total}\n" \
          f"☠ Killed: {dead}\n" \
          f"🩹 Recoveries: {recovered}`"

    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='MarkdownV2')
