from django.urls import path
from order import views

urlpatterns = [
    path("list/", views.order_list, name="order-list"),
    path("<int:pk>/edit/", views.order_edit, name="order-edit"),
    path("<int:pk>/chat/", views.order_chat, name="order-chat"),
    path("<int:pk>/map/", views.order_map, name="order-map"),
]
