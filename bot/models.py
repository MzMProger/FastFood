from django.db import models


class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Log(models.Model):
    chat_id = models.BigIntegerField(primary_key=True)
    messages = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"

    def __str__(self):
        return f"Log chat: {self.chat_id}"
