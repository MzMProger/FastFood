from typing import List

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from bot.models import TelegramUser
import logging

from category.models import Category
from order.models import Order, OrderProduct
from product.models import Product

logger = logging.getLogger(__name__)


def get_telegram_user(chat_id: int):
    try:
        telegram_user = TelegramUser.objects.get(pk=chat_id)
    except TelegramUser.DoesNotExist:
        telegram_user = None
    return telegram_user


def create_telegram_user(chat_id, first_name, last_name, phone_number):
    try:
        TelegramUser.objects.create(
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
    except Exception as e:
        logger.info(f"Error (): {e}")


def get_category_by_name(name: str):
    try:
        category = Category.objects.get(name=name)
    except Category.DoesNotExist:
        category = None
    return category


def get_category_by_id(pk: int):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        category = None
    return category


def get_product_by_name(name: str, category_id: int):
    try:
        product = Product.objects.get(name=name, category_id=category_id)
    except Product.DoesNotExist:
        product = None
    return product


def get_product_by_id(pk: int):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        product = None
    return product


def create_order(chat_id: int, orders: List[dict], comment: str, location, order_type: str, takeaway_time: int):
    try:
        total_price = settings.DELIVERY_PRICE
        telegram_user = TelegramUser.objects.get(pk=chat_id)
        delivery_price = settings.DELIVERY_PRICE if order_type == "delivery" else 0
        order = Order.objects.create(
            telegram_user=telegram_user,
            comment=comment,
            phone_number=telegram_user.phone_number,
            delivery_price=delivery_price,
            total_price=total_price,
            latitude=location.get("latitude", 0),
            longitude=location.get("longitude", 0),
            order_type=order_type,
            takeaway_time=takeaway_time,
        )
        for o in orders:
            op = OrderProduct.objects.create(
                order=order,
                product_id=o.get("product_id"),
                amount=o.get("count"),
            )
            total_price += op.product.price * op.amount
            op.price_per_one = op.product.price
            op.save()

        order.total_price = total_price
        order.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notification",
            {
                "type": "send_notification",
                "value": {
                    "id": order.id,
                    "status": order.status,
                    "order_type": order.order_type,
                    "status_label": order.get_status_display(),
                    "phone_number": order.phone_number,
                }
            }
        )
        return order
    except Exception as e:
        print(e)


def get_active_orders_count():
    try:
        cnt = Order.objects.filter(status__in=["pending", "preparing", "prepared"], order_type="delivery").count()
    except Exception:
        cnt = 0
    return cnt
