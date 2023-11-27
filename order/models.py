from django.db import models

from order.choices import OrderStatus, OrderType
from product.models import Product


class Order(models.Model):
    telegram_user = models.ForeignKey("bot.TelegramUser", on_delete=models.PROTECT)
    products = models.ManyToManyField("product.Product", through="OrderProduct")
    comment = models.TextField(blank=True)
    phone_number = models.CharField(max_length=50)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    delivery_price = models.BigIntegerField(default=0)
    total_price = models.BigIntegerField(default=0)
    status = models.CharField(max_length=255, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    order_type = models.CharField(max_length=255, choices=OrderType.choices, default=OrderType.DELIVERY)
    takeaway_time = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True)


class OrderProduct(models.Model):
    order = models.ForeignKey("order.Order", on_delete=models.PROTECT)
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    price_per_one = models.PositiveIntegerField(default=0)
