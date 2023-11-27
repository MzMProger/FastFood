from pathlib import Path
from django.conf import settings
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from bot import globals as gls, services
from category.models import Category
from product.models import Product


def send_comment(context, chat_id):
    buttons = [
        [KeyboardButton(text=gls.BTN_SKIP)],
        [KeyboardButton(text=gls.BTN_BACK)],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    send_message(
        context=context,
        chat_id=chat_id,
        message=gls.TEXT_SEND_COMMENT,
        reply_markup=reply_markup
    )


def send_message(context, chat_id, message, reply_markup):
    return context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


def send_photo(context, chat_id, photo, caption=None, reply_markup=None):
    context.bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


def send_main_menu(context, chat_id):
    msg = gls.TEXT_MAIN_MENU
    buttons = [
        [
            KeyboardButton(text=gls.BTN_MENU),
        ],
        [
            KeyboardButton(text=gls.BTN_SETTINGS),
            KeyboardButton(text=gls.BTN_MY_ORDERS),
        ],
        [
            KeyboardButton(text=gls.BTN_CART),
        ],
        [
            KeyboardButton(text=gls.BTN_ABOUT),
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    send_message(
        context=context,
        chat_id=chat_id,
        message=msg,
        reply_markup=reply_markup
    )


def send_first_name(context, chat_id):
    msg = gls.TEXT_ENTER_FIRST_NAME
    send_message(
        context=context,
        chat_id=chat_id,
        message=msg,
        reply_markup=ReplyKeyboardRemove(),
    )


def send_last_name(context, chat_id):
    msg = gls.TEXT_ENTER_LAST_NAME
    send_message(
        context=context,
        chat_id=chat_id,
        message=msg,
        reply_markup=ReplyKeyboardRemove(),
    )


def send_phone_number(context, chat_id):
    msg = gls.TEXT_ENTER_PHONE_NUMBER
    send_message(
        context=context,
        chat_id=chat_id,
        message=msg,
        reply_markup=ReplyKeyboardRemove(),
    )


def send_categories(context, chat_id):
    categories = Category.objects.filter(is_active=True).order_by("order")
    buttons = []
    row = []
    is_first_column = True
    for category in categories:
        row.append(KeyboardButton(text=category.name))
        if is_first_column:
            is_first_column = False
        else:
            is_first_column = True
            buttons.append(row)
            row = []
    row.append(KeyboardButton(text=gls.BTN_CART))
    if not is_first_column:
        buttons.append(row)
        row = []
    row.append(KeyboardButton(text=gls.BTN_BACK))
    buttons.append(row)
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    photo_path = Path(__file__).resolve().parent.joinpath("static")
    photo = open(f"{photo_path}/img-min.png", "rb")
    context.bot.send_photo(
        photo=photo,
        chat_id=chat_id,
        caption=gls.TEXT_MENU,
        reply_markup=reply_markup,
    )


def send_products(context, chat_id, category):
    products = Product.objects.filter(category=category, is_active=True)
    buttons = []
    row = []
    is_first_column = True
    for product in products:
        row.append(KeyboardButton(text=product.name))
        if is_first_column:
            is_first_column = False
        else:
            is_first_column = True
            buttons.append(row)
            row = []
    row.append(KeyboardButton(text=gls.BTN_CART))
    if not is_first_column:
        buttons.append(row)
        row = []
    row.append(KeyboardButton(text=gls.BTN_BACK))
    buttons.append(row)
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    send_message(
        context=context,
        chat_id=chat_id,
        message=gls.TEXT_PRODUCTS,
        reply_markup=reply_markup
    )


def send_product(context, chat_id, product):
    buttons = [
        [KeyboardButton(text=gls.BTN_CART)],
        [KeyboardButton(text=gls.BTN_BACK)],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    send_message(
        context=context,
        chat_id=chat_id,
        message=gls.TEXT_CHOOSE_FOLLOWINGS,
        reply_markup=reply_markup
    )

    msg = f"<b>{product.name}</b>\n{product.desc}\nNarxi: {product.price} won"
    buttons = [
        [
            InlineKeyboardButton(
                text=gls.BTN_PRODUCT_COUNT_MINUS, callback_data=f"product_remove_{product.id}_1"
            ),
            InlineKeyboardButton(
                text="1", callback_data=f"product_count_{product.id}"
            ),
            InlineKeyboardButton(
                text=gls.BTN_PRODUCT_COUNT_PLUS, callback_data=f"product_add_{product.id}_1"
            ),
        ],
        [InlineKeyboardButton(
            text=gls.BTN_PRODUCT_ADD_TO_CART, callback_data=f"product_order_{product.id}_1"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        send_photo(
            context=context,
            chat_id=chat_id,
            photo=open(product.image.path, "rb"),
            caption=msg,
            reply_markup=reply_markup
        )
    except Exception as e:
        send_message(
            context=context,
            chat_id=chat_id,
            message=msg,
            reply_markup=reply_markup
        )


def send_cart_product(context, chat_id, orders, message_id=None):
    if orders:
        buttons = [
            [
                InlineKeyboardButton(text="🏃 Olib ketish", callback_data="cart_takeaway"),
                InlineKeyboardButton(text="🚖 Yetkazib berish", callback_data="cart_delivery"),
            ],
            [
                InlineKeyboardButton(text="🗑 Savatni tozalash", callback_data="cart_clean_all"),
            ],
        ]
        products_msg = ""
        products_price = 0
        for order in orders:
            count = order.get("count")
            product = services.get_product_by_id(pk=order.get("product_id"))
            products_price += product.price * count
            count_msg = "".join([gls.NUMBERS_MAP.get(f"{i}", "") for i in str(count)])
            products_msg += f"<b>{count_msg} ✖ {product.category.name} {product.name}</b>\n"
            buttons.append(
                [InlineKeyboardButton(text=f"❌ {product.category.name} {product.name}", callback_data=f"cart_clean_{product.id}")]
            )
        total_price = products_price + settings.DELIVERY_PRICE
        final_msg = f"Savatda:\n{products_msg}Mahsulotlar: {products_price} won\nYetkazib berish: {settings.DELIVERY_PRICE} won\nJami: {total_price} won"

        reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        if message_id:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=final_msg,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            send_message(
                context=context,
                chat_id=chat_id,
                message=final_msg,
                reply_markup=reply_markup
            )
    else:
        send_message(
            context=context,
            chat_id=chat_id,
            message=gls.TEXT_CART_EMPTY,
            reply_markup=None
        )


def send_location(context, chat_id):
    buttons = [
        [KeyboardButton(text=gls.BTN_SEND_LOCATION, request_location=True)],
        [KeyboardButton(text=gls.BTN_BACK)],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    send_message(
        context=context,
        chat_id=chat_id,
        message=gls.TEXT_SEND_LOCATION,
        reply_markup=reply_markup,
    )


def send_takeaway_time(context, chat_id):
    buttons = [
        [KeyboardButton(text=gls.BTN_BACK)],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    send_message(
        context=context,
        chat_id=chat_id,
        message=gls.TEXT_SEND_TAKEAWAY_TIME,
        reply_markup=reply_markup,
    )


def send_verify_order(context, chat_id, order_type):
    buttons = [
        [KeyboardButton(text=gls.BTN_VERIFY_ORDER)],
        [KeyboardButton(text=gls.BTN_BACK)],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    if order_type == "delivery":
        cnt = services.get_active_orders_count()
        if cnt < 11:
            info = f"{cnt} ta"
        else:
            info = f"10 dan ortiq"
        message = f"{gls.TEXT_DELIVERY_INFO}\n{gls.TEXT_DELIVERY_INFO_EXTRA.format(info)}\n{gls.TEXT_VERIFY_ORDER}"
    else:
        message = f"{gls.TEXT_VERIFY_ORDER}"

    send_message(
        context=context,
        chat_id=chat_id,
        message=message,
        reply_markup=reply_markup,
    )


def send_delivery_info(context, chat_id):
    send_message(
        context=context,
        chat_id=chat_id,
        message=gls.TEXT_DELIVERY_INFO,
        reply_markup=ReplyKeyboardRemove(),
    )
