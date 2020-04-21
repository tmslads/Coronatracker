from telegram.ext import Updater, CommandHandler
import commands


with open('token.txt', 'r') as f:
    token = f.read()

updater = Updater(token=token, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler(command='start', callback=commands.start))
dp.add_handler(CommandHandler(command='help', callback=commands.helper))
dp.add_handler(CommandHandler(command='world', callback=commands.world))
dp.add_handler(CommandHandler(command='UAE', callback=commands.uae))


updater.start_polling()
updater.idle()
