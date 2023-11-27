from django.conf import settings
from telegram import (
    bot,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    messagequeue as mq
)
from bot import globals as gls, services
from bot.decorators import active_users_allowed, active_users_allowed_inline
from bot import sends
from bot.user_data import UserData
from order.models import Order, OrderProduct


class MQBot(bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_message(*args, **kwargs)

    @mq.queuedmessage
    def forward_message(self, *args, **kwargs):
        return super(MQBot, self).forward_message(*args, **kwargs)

    @mq.queuedmessage
    def delete_message(self, chat_id, message_id, timeout=None, **kwargs):
        return super(MQBot, self).delete_message(chat_id, message_id, timeout, **kwargs)

    @mq.queuedmessage
    def send_photo(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_photo(*args, **kwargs)

    @mq.queuedmessage
    def send_video(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_video(*args, **kwargs)

    @mq.queuedmessage
    def send_audio(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_audio(*args, **kwargs)

    @mq.queuedmessage
    def send_document(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_document(*args, **kwargs)

    @mq.queuedmessage
    def send_voice(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup` OPTIONAL arguments"""
        return super(MQBot, self).send_voice(*args, **kwargs)


@active_users_allowed
def start_handler(update, context):
    chat_id = update.message.from_user.id
    telegram_user = services.get_telegram_user(chat_id=chat_id)
    user_log = UserData(context, update)

    if telegram_user:
        sends.send_main_menu(context, chat_id)
        user_log.change_state({"state": gls.States.MAIN_MENU})
        return

    if not user_log.user_data.get("first_name"):
        sends.send_first_name(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.REGISTRATION_FIRST_NAME})
        return

    if not user_log.user_data.get("last_name"):
        sends.send_last_name(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.REGISTRATION_LAST_NAME})
        return

    if not user_log.user_data.get("phone_number"):
        sends.send_phone_number(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.REGISTRATION_PHONE_NUMBER})
        return


@active_users_allowed
def message_handler(update, context):
    chat_id = update.message.from_user.id
    message = update.message.text
    user_log = UserData(context, update)
    state = user_log.user_data.get("state")

    if state == gls.States.REGISTRATION_FIRST_NAME:
        user_log.change_state({"first_name": message})
        sends.send_last_name(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.REGISTRATION_LAST_NAME})
        return

    elif state == gls.States.REGISTRATION_LAST_NAME:
        user_log.change_state({"last_name": message})
        sends.send_phone_number(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.REGISTRATION_PHONE_NUMBER})
        return

    elif state == gls.States.REGISTRATION_PHONE_NUMBER:
        user_log.change_state({"phone_number": message})
        services.create_telegram_user(
            chat_id=chat_id,
            first_name=user_log.user_data.get("first_name"),
            last_name=user_log.user_data.get("last_name"),
            phone_number=user_log.user_data.get("phone_number"),
        )
        sends.send_main_menu(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.MAIN_MENU})
        return

    elif state == gls.States.MAIN_MENU:
        if message == gls.BTN_MENU:
            sends.send_categories(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.MENU})
            return

        elif message == gls.BTN_MY_ORDERS:
            telegram_user = services.get_telegram_user(chat_id=chat_id)
            orders = Order.objects.filter(telegram_user=telegram_user).order_by("-created_at")[:5]
            for order in orders:
                products_msg = ""
                products_price = 0
                order_products = OrderProduct.objects.filter(order=order)
                for order_product in order_products:
                    products_price += order_product.product.price * order_product.amount
                    count_msg = "".join([gls.NUMBERS_MAP.get(f"{i}", "") for i in str(order_product.amount)])
                    products_msg += f"<b>{count_msg} ✖ {order_product.product.name}</b>\n"
                if order.order_type == "delivery":
                    total_price = products_price + settings.DELIVERY_PRICE
                    final_msg = f"Buyurtma raqami: {order.id}\n" \
                                f"Turi: {order.get_order_type_display()}\n" \
                                f"Holati: {order.get_status_display()}\n\n" \
                                f"{products_msg}\n" \
                                f"Mahsulotlar: {products_price} won\n" \
                                f"Yetkazib berish: {settings.DELIVERY_PRICE} won\n" \
                                f"Jami: {total_price} won"
                else:
                    total_price = products_price
                    final_msg = f"Buyurtma raqami: {order.id}\n" \
                                f"Turi: {order.get_order_type_display()}\n" \
                                f"Holati: {order.get_status_display()}\n\n" \
                                f"{products_msg}\n" \
                                f"Mahsulotlar: {products_price} won\n" \
                                f"Jami: {total_price} won"
                sends.send_message(
                    context=context,
                    chat_id=chat_id,
                    message=final_msg,
                    reply_markup=None
                )

        elif message == gls.BTN_SETTINGS:
            buttons = [
                [KeyboardButton(text=gls.BTN_BACK)]
            ]
            reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
            sends.send_message(
                context=context,
                chat_id=chat_id,
                message=gls.TEXT_SETTINGS,
                reply_markup=reply_markup
            )
            user_log.change_state({"state": gls.States.SETTINGS})
            return

        elif message == gls.BTN_ABOUT:
            sends.send_message(
                context=context,
                chat_id=chat_id,
                message=f"{gls.TEXT_ABOUT_BOT} ☎ {settings.PHONE_NUMBER}",
                reply_markup=None
            )
            return

        elif message == gls.BTN_CART:
            orders = user_log.user_data.get("orders")
            sends.send_cart_product(context=context, chat_id=chat_id, orders=orders)

        else:
            sends.send_main_menu(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.MAIN_MENU})
            return

    elif state == gls.States.MENU:
        if message == gls.BTN_BACK:
            sends.send_main_menu(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.MAIN_MENU})
            return

        elif message == gls.BTN_CART:
            orders = user_log.user_data.get("orders")
            sends.send_cart_product(context=context, chat_id=chat_id, orders=orders)
            return

        else:
            category = services.get_category_by_name(name=message)
            if category:
                sends.send_products(context=context, chat_id=chat_id, category=category)
                user_log.change_state({"state": gls.States.PRODUCTS, "category_id": category.id})
            return

    elif state == gls.States.SETTINGS:
        if message == gls.BTN_BACK:
            sends.send_main_menu(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.MAIN_MENU})
            return
        return

    elif state == gls.States.PRODUCTS:
        if message == gls.BTN_BACK:
            sends.send_categories(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.MENU})
            return

        elif message == gls.BTN_CART:
            orders = user_log.user_data.get("orders")
            sends.send_cart_product(context=context, chat_id=chat_id, orders=orders)
            return

        else:
            category_id = user_log.user_data.get("category_id", None)
            product = services.get_product_by_name(name=message, category_id=category_id)
            if product:
                sends.send_product(context=context, chat_id=chat_id, product=product)
                user_log.change_state({"state": gls.States.PRODUCTS})
            else:
                sends.send_message(
                    context=context,
                    chat_id=chat_id,
                    message=gls.TEXT_PRODUCT_NOT_FOUND,
                    reply_markup=None
                )
            return

    elif state == gls.States.ORDER:
        order_type = user_log.user_data.get("order_type")
        if order_type == "delivery":
            if message == gls.BTN_BACK:
                if user_log.user_data.get("location"):
                    if user_log.user_data.get("comment") is None:
                        user_log.change_state({"location": None})
                        sends.send_location(
                            context=context,
                            chat_id=chat_id
                        )
                        return

                    else:
                        user_log.change_state({"comment": None})
                        sends.send_comment(context=context, chat_id=chat_id)
                        return

                else:
                    sends.send_main_menu(context=context, chat_id=chat_id)
                    user_log.change_state({"state": gls.States.MAIN_MENU})
                    return

            elif message == gls.BTN_SKIP:
                if user_log.user_data.get("location"):
                    user_log.change_state({"comment": ""})
                    sends.send_verify_order(
                        context=context,
                        chat_id=chat_id,
                        order_type=order_type
                    )
                return

            elif message == gls.BTN_VERIFY_ORDER:
                orders = user_log.user_data.get("orders", [])
                location = user_log.user_data.get("location", {})
                comment = user_log.user_data.get("comment", "")
                order_type = "delivery"
                create_and_send_order(chat_id, comment, context, order_type, orders, location)
                user_log.change_state({
                    "state": gls.States.MAIN_MENU,
                    "orders": None,
                    "location": None,
                    "comment": None
                })
                sends.send_main_menu(context=context, chat_id=chat_id)
                return

            else:
                if user_log.user_data.get("location") and user_log.user_data.get("comment") is None:
                    user_log.change_state({"comment": message})
                    sends.send_verify_order(
                        context=context,
                        chat_id=chat_id,
                        order_type=order_type
                    )
                return

        elif order_type == "takeaway":
            if message == gls.BTN_BACK:
                if user_log.user_data.get("takeaway_time") is not None:
                    if user_log.user_data.get("comment") is None:
                        user_log.change_state({"takeaway_time": None})
                        sends.send_takeaway_time(
                            context=context,
                            chat_id=chat_id
                        )
                        return

                    else:
                        user_log.change_state({"comment": None})
                        sends.send_comment(context=context, chat_id=chat_id)
                        return

                else:
                    sends.send_main_menu(context=context, chat_id=chat_id)
                    user_log.change_state({"state": gls.States.MAIN_MENU})
                    return

            elif message == gls.BTN_SKIP:
                if user_log.user_data.get("takeaway_time") is not None:
                    user_log.change_state({"comment": ""})
                    sends.send_verify_order(
                        context=context,
                        chat_id=chat_id,
                        order_type=order_type
                    )
                return

            elif message == gls.BTN_VERIFY_ORDER:
                orders = user_log.user_data.get("orders", [])
                comment = user_log.user_data.get("comment", "")
                takeaway_time = user_log.user_data.get("takeaway_time", 0)
                location = {}
                order_type = "take_away"
                create_and_send_order(chat_id, comment, context, order_type, orders, location, takeaway_time)
                user_log.change_state({
                    "state": gls.States.MAIN_MENU,
                    "orders": None,
                    "takeaway_time": None,
                    "comment": None
                })
                sends.send_main_menu(context=context, chat_id=chat_id)
                return

            else:
                if user_log.user_data.get("takeaway_time") is not None:
                    if user_log.user_data.get("comment") is None:
                        user_log.change_state({"comment": message})
                        sends.send_verify_order(
                            context=context,
                            chat_id=chat_id,
                            order_type=order_type
                        )
                    return
                else:
                    try:
                        takeaway_time = int(message)
                        user_log.change_state({"takeaway_time": takeaway_time})
                        sends.send_comment(context=context, chat_id=chat_id)
                    except Exception as e:
                        sends.send_takeaway_time(context=context, chat_id=chat_id)
                return


@active_users_allowed_inline
def callback_query_handler(update, context):
    query = update.callback_query
    chat_id = query.from_user.id
    data_sp = query.data.split("_")
    message_id = update.callback_query.message.message_id
    user_log = UserData(context, update)
    state = user_log.user_data.get("state")

    if state == gls.States.PRODUCTS and data_sp[0] == 'product':
        if data_sp[1] == "order":
            orders = user_log.user_data.get("orders")
            if orders is None:
                orders = []
            is_new = True
            for index, order in enumerate(orders):
                if order.get("product_id") == int(data_sp[2]):
                    order["count"] = order.get("count", 0) + int(data_sp[3])
                    orders[index] = order
                    is_new = False
                    break
            if is_new:
                order = {
                    "product_id": int(data_sp[2]),
                    "count": int(data_sp[3]),
                }
                orders.append(order)
            context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
            user_log.change_state({"orders": orders})
            product = services.get_product_by_id(pk=int(data_sp[2]))
            if product and product.category:
                sends.send_products(context=context, chat_id=chat_id, category=product.category)
                user_log.change_state({"state": gls.States.PRODUCTS})
            return

        elif data_sp[1] == "add":
            count = int(data_sp[3])
            count += 1
            buttons = [
                [
                    InlineKeyboardButton(
                        text=gls.BTN_PRODUCT_COUNT_MINUS, callback_data=f"product_remove_{data_sp[2]}_{count}"
                    ),
                    InlineKeyboardButton(
                        text=f"{count}", callback_data=f"product_count_{data_sp[2]}"
                    ),
                    InlineKeyboardButton(
                        text=gls.BTN_PRODUCT_COUNT_PLUS, callback_data=f"product_add_{data_sp[2]}_{count}"
                    ),
                ],
                [InlineKeyboardButton(
                    text=gls.BTN_PRODUCT_ADD_TO_CART, callback_data=f"product_order_{data_sp[2]}_{count}"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup
            )

        elif data_sp[1] == "remove":
            count = int(data_sp[3])
            if count == 1:
                return
            count -= 1
            buttons = [
                [
                    InlineKeyboardButton(
                        text=gls.BTN_PRODUCT_COUNT_MINUS, callback_data=f"product_remove_{data_sp[2]}_{count}"
                    ),
                    InlineKeyboardButton(
                        text=f"{count}", callback_data=f"product_count_{data_sp[2]}"
                    ),
                    InlineKeyboardButton(
                        text=gls.BTN_PRODUCT_COUNT_PLUS, callback_data=f"product_add_{data_sp[2]}_{count}"
                    ),
                ],
                [InlineKeyboardButton(
                    text=gls.BTN_PRODUCT_ADD_TO_CART, callback_data=f"product_order_{data_sp[2]}_{count}"
                )]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup
            )
    
    elif data_sp[0] == "cart":
        if data_sp[1] == "delivery":
            context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
            sends.send_location(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.ORDER, "order_type": "delivery"})

        elif data_sp[1] == "takeaway":
            context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
            sends.send_takeaway_time(context=context, chat_id=chat_id)
            user_log.change_state({"state": gls.States.ORDER, "order_type": "takeaway"})

        elif data_sp[1] == "clean":
            if data_sp[2] == "all":
                user_log.change_state({"orders": []})
                context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=gls.TEXT_CART_EMPTY,
                    reply_markup=None
                )
            else:
                product_id = int(data_sp[2])
                orders = user_log.user_data.get("orders", [])
                for index, order in enumerate(orders):
                    if order.get("product_id") == product_id:
                        orders.pop(index)
                        break
                user_log.change_state({"orders": orders})
                sends.send_cart_product(context=context, chat_id=chat_id, orders=orders, message_id=message_id)


@active_users_allowed
def contact_handler(update, context):
    user_log = UserData(context, update)
    state = user_log.user_data.get('state')
    chat_id = update.message.from_user.id
    contact = update.message.contact

    if contact.user_id == chat_id and state == gls.States.REGISTRATION_PHONE_NUMBER:
        user_log.change_state({"phone_number": contact.phone_number})
        services.create_telegram_user(
            chat_id=chat_id,
            first_name=user_log.user_data.get("first_name"),
            last_name=user_log.user_data.get("last_name"),
            phone_number=user_log.user_data.get("phone_number"),
        )
        sends.send_main_menu(context=context, chat_id=chat_id)
        user_log.change_state({"state": gls.States.MAIN_MENU})
        return


@active_users_allowed
def location_handler(update, context):
    user_log = UserData(context, update)
    state = user_log.user_data.get('state')
    chat_id = update.message.from_user.id
    geo = update.message.location

    if state == gls.States.ORDER:
        location = {"longitude": geo.longitude, "latitude": geo.latitude}
        user_log.change_state({"location": location})
        sends.send_comment(context=context, chat_id=chat_id)
        return


def create_and_send_order(chat_id, comment, context, order_type, orders, location, takeaway_time=0):
    order = services.create_order(
        chat_id=chat_id,
        comment=comment,
        location=location,
        orders=orders,
        order_type=order_type,
        takeaway_time=takeaway_time
    )
    products_msg = ""
    products_price = 0
    for o in orders:
        count = o.get("count")
        product = services.get_product_by_id(pk=o.get("product_id"))
        products_price += product.price * count
        count_msg = "".join([gls.NUMBERS_MAP.get(f"{i}", "") for i in str(count)])
        products_msg += f"<b>{count_msg} ✖ {product.name}</b>\n"
    if order_type == "delivery":
        total_price = products_price + settings.DELIVERY_PRICE
        final_msg = f"Buyurtma raqami: {order.id}\n" \
                    f"Turi: {order.get_order_type_display()}\n" \
                    f"Holati: {order.get_status_display()}\n\n" \
                    f"{products_msg}\n" \
                    f"Mahsulotlar: {products_price} won\n" \
                    f"Yetkazib berish: {settings.DELIVERY_PRICE} won\n" \
                    f"Jami: {total_price} won"
    else:
        total_price = products_price
        final_msg = f"Buyurtma raqami: {order.id}\n" \
                    f"Turi: {order.get_order_type_display()}\n" \
                    f"Holati: {order.get_status_display()}\n\n" \
                    f"{products_msg}\n" \
                    f"Mahsulotlar: {products_price} won\n" \
                    f"Jami: {total_price} won"
    sends.send_message(
        context=context,
        chat_id=chat_id,
        message=final_msg,
        reply_markup=ReplyKeyboardRemove()
    )
    send_new_order_to_admin(context=context, order_id=order.id)


def send_new_order_to_admin(context, order_id):
    chat_ids = settings.ADMIN_CHAT_IDS.split(",")
    for chat_id in chat_ids:
        if chat_id:
            try:
                sends.send_message(
                    context=context,
                    chat_id=chat_id,
                    message=f"Yangi buyurtma № {order_id}",
                    reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                pass
