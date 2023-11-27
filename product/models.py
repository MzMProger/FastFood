from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True)
    price = models.BigIntegerField(default=0)
    image = models.ImageField(upload_to="images/")
    category = models.ForeignKey("category.Category", null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        unique_together = (("name", "category"), )

    def __str__(self):
        return f"{self.name}"
