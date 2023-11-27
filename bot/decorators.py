from django.conf import settings
from telegram import ReplyKeyboardRemove
from bot import globals as gls, sends

from bot import services


def active_users_allowed(func):
    def inner(update, context):
        chat_id = update.message.from_user.id
        telegram_user = services.get_telegram_user(chat_id=chat_id)
        if telegram_user is not None:
            if not telegram_user.is_active:
                sends.send_message(
                    context=context,
                    chat_id=chat_id,
                    message=f"{gls.TEXT_YOU_ARE_BLOCKED}\n☎ {settings.PHONE_NUMBER}",
                    reply_markup=ReplyKeyboardRemove()
                )
                return False
        return func(update, context)
    return inner


def active_users_allowed_inline(func):
    def inner(update, context):
        chat_id = update.callback_query.from_user.id
        telegram_user = services.get_telegram_user(chat_id=chat_id)
        if telegram_user is not None:
            if not telegram_user.is_active:
                sends.send_message(
                    context=context,
                    chat_id=chat_id,
                    message=f"{gls.TEXT_YOU_ARE_BLOCKED}\n☎ {settings.PHONE_NUMBER}",
                    reply_markup=ReplyKeyboardRemove()
                )
                return False
        return func(update, context)
    return inner
