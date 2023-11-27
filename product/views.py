from django.core.paginator import Paginator
from django.db.models import Q
from django.template.response import TemplateResponse

from category.models import Category
from product.models import Product
from product.forms import ProductForm
from django.shortcuts import redirect, get_object_or_404, reverse
from core.views import login_required, check_users_permissions
from django.http import JsonResponse


@login_required
@check_users_permissions(only_superuser=True)
def product_list(request):
    search = request.GET.get("search", "")
    category_id = int(request.GET.get("category_id", 0))

    products = Product.objects.all().order_by("category", "pk")

    if search:
        products = products.filter(Q(name__contains=search))

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all().order_by("order")
    context = {
        "products": products,
        "categories": categories,
        "search": search,
        "category_id": category_id
    }
    return TemplateResponse(request, "product/list.html", context)


@login_required
@check_users_permissions(only_superuser=True)
def product_create(request):
    model = None
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("dashboard:product-list")
        else:
            print(form.errors)
    context = {
        "model": model,
        "form": form
    }
    return TemplateResponse(request, "product/form.html", context)


@login_required
@check_users_permissions(only_superuser=True)
def product_edit(request, pk=None):
    model = Product.objects.get(pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("dashboard:product-list")
        else:
            print(form.errors)
    context = {
        "model": model,
        "form": form
    }
    return TemplateResponse(request, "product/form.html", context)


@login_required
@check_users_permissions(only_superuser=True)
def product_delete(request, pk=None):
    model = get_object_or_404(Product, pk=pk)
    model.delete()
    return JsonResponse({"url": reverse("dashboard:product-list")})
