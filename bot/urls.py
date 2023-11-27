from django.urls import path
from bot import views

urlpatterns = [
    path("list/", views.telegram_user_list, name="telegram-user-list"),
    path("data/list/", views.telegram_user_data_list, name="telegram-user-data-list"),
    path("<int:pk>/activation/", views.telegram_user_activation, name="telegram-user-activation"),
    path("<int:pk>/detail/", views.telegram_user_detail, name="telegram-user-detail"),
]
