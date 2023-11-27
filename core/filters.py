from django import template

from order.models import OrderProduct

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter('subtract')
def subtract(a, b):
    return a - b


@register.filter('order_products')
def order_products(order):
    ops = OrderProduct.objects.filter(order=order)
    return ops
