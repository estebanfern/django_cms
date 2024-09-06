from unicodedata import category

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from category.models import Category
from content.models import Content


# Create your views here.
def categories_by_type(request, type):
    categories = Category.objects.filter(type=type)
    types = {
        'Pago' : 'Categorias de Pago',
        'Publico' : 'Categorias Públicas',
        'Suscriptor' : 'Categorias de Suscriptor',
    }
    return render(request, 'category/categories_by_type.html', {'categories': categories, 'type': types[type]})
