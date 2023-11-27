from django.urls import path
from category import views

urlpatterns = [
    path("list/", views.category_list, name="category-list"),
    path("create/", views.category_create, name="category-create"),
    path("<int:pk>/edit/", views.category_edit, name="category-edit"),
    path("<int:pk>/delete/", views.category_delete, name="category-delete"),
]
