from django.contrib import admin
from order.models import Order, OrderProduct

admin.site.register(Order)
admin.site.register(OrderProduct)
