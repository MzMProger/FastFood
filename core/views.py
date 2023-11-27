from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required as _login_required
from django.contrib import auth, messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
from bot.models import TelegramUser
from order.choices import OrderStatus
from order.models import Order


def login_required(f):
    return _login_required(f, login_url="dashboard:login")


def check_users_permissions(only_superuser=True):
    def inner(func):
        def wrapper(*args, **kwargs):
            if only_superuser:
                try:
                    if args[0].user.is_superuser:
                        return func(*args, **kwargs)
                except Exception:
                    pass
            return HttpResponse(status=404)
        return wrapper
    return inner


def dashboard_login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard:dashboard')
            else:
                return redirect('dashboard:order-list')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


@login_required
def index(request):
    if request.user.is_superuser:
        all_users_count = TelegramUser.objects.count() or 0
        all_orders_count = Order.objects.filter(status=OrderStatus.DELIVERED.value).count() or 0
        today_orders_count = Order.objects.filter(
            status=OrderStatus.DELIVERED.value,
            created_at__day=timezone.now().day,
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year,
        ).count() or 0
        monthly_sell_amount = Order.objects.filter(
            status=OrderStatus.DELIVERED.value,
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year,
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        context = {
            "all_users_count": all_users_count,
            "all_orders_count": all_orders_count,
            "today_orders_count": today_orders_count,
            "monthly_sell_amount": monthly_sell_amount,
        }
    else:
        context = {}
    return render(request, 'index.html', context)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('dashboard:dashboard', )
