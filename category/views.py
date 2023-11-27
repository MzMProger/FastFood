from django.template.response import TemplateResponse
from category.models import Category
from category.forms import CategoryForm
from django.shortcuts import redirect, get_object_or_404, reverse
from core.views import login_required, check_users_permissions
from django.http import JsonResponse


@login_required
@check_users_permissions(only_superuser=True)
def category_list(request):
    categories = Category.objects.all().order_by("order")
    context = {
        "categories": categories
    }
    return TemplateResponse(request, "category/list.html", context)


@login_required
@check_users_permissions(only_superuser=True)
def category_create(request):
    model = None
    form = CategoryForm(request.POST or None)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("dashboard:category-list")
        else:
            print(form.errors)
    context = {
        "model": model,
        "form": form
    }
    return TemplateResponse(request, "category/form.html", context)


@login_required
@check_users_permissions(only_superuser=True)
def category_edit(request, pk=None):
    model = Category.objects.get(pk=pk)
    form = CategoryForm(request.POST or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("dashboard:category-list")
        else:
            print(form.errors)
    context = {
        "model": model,
        "form": form,
    }
    return TemplateResponse(request, "category/form.html", context)


@login_required
@check_users_permissions(only_superuser=True)
def category_delete(request, pk=None):
    model = get_object_or_404(Category, pk=pk)
    model.delete()
    return JsonResponse({"url": reverse("dashboard:category-list")})
