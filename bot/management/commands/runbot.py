import os.path
from django.core.management.base import BaseCommand
from telegram import BotCommand
from telegram.ext import (Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, messagequeue as mq)
from telegram.utils.request import Request
from bot.handlers import MQBot, start_handler, message_handler, callback_query_handler, contact_handler, \
    location_handler
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Command(BaseCommand):
    help = 'Runs telegram bot'

    def handle(self, *args, **kwargs):
        q = mq.MessageQueue(
            all_burst_limit=3,
            all_time_limit_ms=3000
        )
        request = Request(con_pool_size=36)
        bot = MQBot(token=settings.BOT_TOKEN, request=request, mqueue=q)
        bot.set_my_commands(
            commands=[
                BotCommand("/start", "Boshlash yoki Asosiy menyu komandasi")
            ]
        )
        updater = Updater(bot=bot, use_context=True, workers=32)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler(command="start", callback=start_handler))
        dispatcher.add_handler(CallbackQueryHandler(callback=callback_query_handler))
        dispatcher.add_handler(MessageHandler(filters=Filters.contact, callback=contact_handler))
        dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=location_handler))
        dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=message_handler))
        updater.start_polling()
        updater.idle()
