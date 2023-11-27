import json
import logging
from threading import Thread
from queue import Queue
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, TelegramError
from bot.handlers import (
    MQBot,
    start_handler,
    callback_query_handler,
    contact_handler,
    location_handler,
    message_handler
)
from django.http.response import JsonResponse
from telegram.ext import (
    messagequeue as mq,
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters
)
from telegram.utils.request import Request


@csrf_exempt
def hook(request):
    q = mq.MessageQueue(
        all_burst_limit=3,
        all_time_limit_ms=3000
    )
    request_bot = Request(con_pool_size=36)
    bot = MQBot(settings.BOT_TOKEN, request=request_bot, mqueue=q)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        logging.warning('Telegram bot <{}> receive invalid request : {}'.format(bot.username, repr(request)))
        return JsonResponse({})

    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue, use_context=True)
    dispatcher.add_handler(CommandHandler(command="start", callback=start_handler))
    dispatcher.add_handler(CallbackQueryHandler(callback=callback_query_handler))
    dispatcher.add_handler(MessageHandler(filters=Filters.contact, callback=contact_handler))
    dispatcher.add_handler(MessageHandler(filters=Filters.location, callback=location_handler))
    dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=message_handler))

    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    try:
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        logging.debug('Bot <{}> : Processed update {}'.format(bot.username, update))
    except TelegramError as te:
        logging.warning("Bot <{}> : Error was raised while processing Update.".format(bot.username))
        dispatcher.dispatch_error(update, te)

    return JsonResponse({})
