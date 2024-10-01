from unicodedata import category

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from category.models import Category
from content.models import Content


# Create your views here.
def categories_by_type(request, type):
    """
    Vista para obtener y renderizar las categorías filtradas por tipo.

    Esta vista filtra las categorías en función del tipo proporcionado y las muestra en una plantilla específica,
    junto con una descripción legible del tipo.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :param type: El tipo de categoría que se desea filtrar ('Pago', 'Publico', 'Suscriptor').
    :type type: str

    :return: Renderiza la plantilla 'category/categories_by_type.html' con las categorías filtradas y el tipo legible.
    :rtype: HttpResponse

    :raises KeyError: Si el tipo proporcionado no está en los tipos disponibles ('Pago', 'Publico', 'Suscriptor').
    """
    categories = Category.objects.filter(type=type)
    types = {
        'Pago' : 'Categorias de Pago',
        'Publico' : 'Categorias Públicas',
        'Suscriptor' : 'Categorias de Suscriptor',
    }
    return render(request, 'category/categories_by_type.html', {'categories': categories, 'type': types[type]})
