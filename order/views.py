from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.http.response import JsonResponse
from telegram import bot

from order.choices import OrderStatus
from order.models import Order, OrderProduct
from order.forms import OrderForm, OrderChatForm
from django.shortcuts import redirect, get_object_or_404, reverse
from core.views import login_required


@login_required
def order_list(request):
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 15))
    status = request.GET.get("status", "")
    orders = Order.objects.all().order_by("-created_at")
    if status:
        orders = orders.filter(status=status)

    paginator = Paginator(orders, per_page)
    orders = paginator.page(page)
    context = {
        "orders": orders,
        "per_page": per_page,
        "status": status
    }
    return TemplateResponse(request, "order/list.html", context)


@login_required
def order_edit(request, pk=None):
    model = Order.objects.get(pk=pk)
    order_products = OrderProduct.objects.filter(order=model)
    old_status = model.status
    form = OrderForm(request.POST or None, instance=model)
    message = ""
    if request.POST:
        if form.is_valid():
            res = form.save(old_status=old_status)
            if res:
                msg = get_status_message(status=res.status)
                msg = msg.format(res.id)
                bot.Bot(token=settings.BOT_TOKEN).send_message(
                    chat_id=res.telegram_user.chat_id,
                    text=msg,
                    parse_mode="HTML"
                )
                return redirect("dashboard:order-list")
            else:
                message = f"{model.get_status_display()} ga o'zgartirib bolmaydi! Ketma-ketlikni to'g'ri amalga oshiring!"
        else:
            print(form.errors)
    context = {
        "model": model,
        "form": form,
        "message": message,
        "order_products": order_products
    }
    return TemplateResponse(request, "order/form.html", context)


@login_required
def order_chat(request, pk=None):
    model = Order.objects.get(pk=pk)
    form = OrderChatForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            msg = form.cleaned_data.get("text", "")
            bot.Bot(token=settings.BOT_TOKEN).send_message(
                chat_id=model.telegram_user.chat_id,
                text=msg,
                parse_mode="HTML"
            )
            return redirect("dashboard:order-list")
        else:
            print(form.errors)
    context = {
        "model": model,
        "form": form,
    }
    return TemplateResponse(request, "order/chat.html", context)


@login_required
def order_map(request, pk=None):
    model = Order.objects.get(pk=pk)
    context = {
        "model": model,
        "KAKAO_MAP_APP_KEY": settings.KAKAO_MAP_APP_KEY,
    }
    return TemplateResponse(request, "order/map.html", context)


def get_status_message(status):
    status_change_map = {
        OrderStatus.DENIED.value: "<b>Buyurtmangiz №{} bekor qilindi!</b>",
        OrderStatus.PREPARING.value: "<b>Buyurtmangiz  №{} tayyorlanish jarayonida!</b>",
        OrderStatus.PREPARED.value: "<b>Buyurtmangiz  №{} tayyor!</b>",
        OrderStatus.DELIVERING.value: "<b>Buyurtmangiz  №{} yetkazib berish jarayonida! 20 daqiqa ichida yetkazib beriladi!</b>",
        OrderStatus.DELIVERED.value: "<b>Buyurtmangiz  №{} topshirildi. Yoqibli ishtaha!</b>",
    }
    return status_change_map.get(status, "")


