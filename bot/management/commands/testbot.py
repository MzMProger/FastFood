from telegram.ext import Updater, CommandHandler
import json
# Define a function to handle the /start command
def start(update, context):
    print(update.to_json())
    # Send a welcome message to the user
    # context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! Welcome to my bot.")

# Create an instance of the Updater class and pass in your bot's token
updater = Updater(token='1109285514:AAGXeoZnQH7lxk6wVOutx_dzz6LCFGB0dkQ', use_context=True)

# Get the Dispatcher object from the Updater instance
dispatcher = updater.dispatcher

# Add a CommandHandler to the dispatcher for the /start command
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Start the bot
updater.start_polling()