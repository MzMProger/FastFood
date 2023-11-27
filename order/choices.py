from django.db import models


class OrderStatus(models.TextChoices):
    PENDING = ("pending", "Yangi")
    DENIED = ("denied", "Bekor qilindi")
    PREPARING = ("preparing", "Tayyorlash jarayonida")
    PREPARED = ("prepared", "Tayyor")
    DELIVERING = ("delivering", "Kuryerda")
    DELIVERED = ("delivered", "Buyurtma topshirildi")


class OrderType(models.TextChoices):
    DELIVERY = ("delivery", "Yetkazib berish")
    TAKE_AWAY = ("take_away", "Olib ketish")
