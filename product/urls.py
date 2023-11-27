from django.urls import path
from product import views

urlpatterns = [
    path("list/", views.product_list, name="product-list"),
    path("create/", views.product_create, name="product-create"),
    path("<int:pk>/edit/", views.product_edit, name="product-edit"),
    path("<int:pk>/delete/", views.product_delete, name="product-delete"),
]
