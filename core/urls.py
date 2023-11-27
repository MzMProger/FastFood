from django.conf.urls import include
from django.urls import path
from core import views
from category import urls as category_urls
from product import urls as product_urls
from bot import urls as telegram_user_urls
from order import urls as order_urls

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("login/", views.dashboard_login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("category/", include(category_urls)),
    path("product/", include(product_urls)),
    path("telegram-user/", include(telegram_user_urls)),
    path("order/", include(order_urls)),
]
