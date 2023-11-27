from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.SmallIntegerField(default=1)
    parent = models.ForeignKey("self", null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"
