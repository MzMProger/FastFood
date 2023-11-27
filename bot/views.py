from django.template.response import TemplateResponse
from bot.models import TelegramUser
from django.http.response import JsonResponse
from core.views import login_required, check_users_permissions
from django.shortcuts import reverse, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from order.models import Order


@login_required
@check_users_permissions(only_superuser=True)
def telegram_user_list(request):
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 25))
    search = request.GET.get("search", "")
    order_by = int(request.GET.get("order_by", 0))

    telegram_users = TelegramUser.objects.all().order_by("first_name")

    if search:
        telegram_users = telegram_users.filter(
            Q(chat_id__contains=search) |
            Q(first_name__contains=search) |
            Q(last_name__contains=search) |
            Q(phone_number__contains=search)
        )

    # if order_by:
    #     telegram_users = telegram_users.order_by("created_at")

    paginator = Paginator(telegram_users, per_page)
    telegram_users = paginator.page(page)

    ctx = {
        "telegram_users": telegram_users,
        "per_page": per_page,
        "search": search,
        "order_by": order_by
    }
    return TemplateResponse(request, "telegram_user/list.html", ctx)


@login_required
@check_users_permissions(only_superuser=True)
def telegram_user_data_list(request):
    if request.GET:
        json_data = []
        draw = request.GET.getlist('draw')
        search = request.GET.getlist('search[value]')
        length = int(request.GET.getlist('length')[0])
        start = int(request.GET.getlist('start')[0])
        column = int(request.GET.getlist('order[0][column]')[0])

        if search[0]:
            telegram_users = TelegramUser.objects.filter(
                Q(chat_id__contains=search) |
                Q(first_name__contains=search) |
                Q(last_name__contains=search) |
                Q(phone_number__contains=search)
            )
        else:
            telegram_users = TelegramUser.objects.all()

        if len(telegram_users) >= start:
            telegram_users = telegram_users[start:(length + start)]

        for telegram_user in telegram_users:
            json_data.append([
                telegram_user.chat_id,
                telegram_user.first_name,
                telegram_user.last_name,
                telegram_user.phone_number,
            ])

        if request.GET.getlist('order[0][dir]')[0] == 'desc':
            json_data = sorted(json_data, key=lambda x: str(x[column]).lower(), reverse=True)

        elif request.GET.getlist('order[0][dir]')[0] == 'asc':
            json_data = sorted(json_data, key=lambda x: str(x[column]).lower())

        response = {
            "draw": draw,
            "recordsTotal": len(telegram_users),
            "recordsFiltered": len(telegram_users),
            "data": json_data
        }
        return JsonResponse(response)


@login_required
@check_users_permissions(only_superuser=True)
def telegram_user_activation(request, pk):
    tg_user = get_object_or_404(TelegramUser, pk=pk)
    tg_user.is_active = not tg_user.is_active
    tg_user.save()
    return JsonResponse({
        "url": reverse("dashboard:telegram-user-list")
    })


@login_required
@check_users_permissions(only_superuser=True)
def telegram_user_detail(request, pk):
    telegram_user = get_object_or_404(TelegramUser, pk=pk)
    orders = Order.objects.filter(telegram_user=telegram_user).order_by("-id")
    ctx = {
        "model": telegram_user,
        "orders": orders
    }
    return TemplateResponse(request, "telegram_user/view.html", ctx)
