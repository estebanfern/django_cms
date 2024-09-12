from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from category.models import Category
from content.models import Content
from django.contrib import messages


# Create your views here.

def home_view(request):
    cat_query = request.GET.get('cat')
    category = None
    query = request.GET.get('query')
    contents = Content.objects.filter(is_active=True, state=Content.StateChoices.publish).select_related('category', 'autor').order_by('-date_create')

    # Si se busco una categoria, verificar si el usuario está logueado en caso de que no sea categoria publica
    # si no está loguead, redirigirle al login con un mensaje
    # TODO: suscripciones a categorias de pago
    # UPDATE: se deja buscar a cualquiera nomas, hasta la previsualizacion
    if cat_query:
        category = get_object_or_404(Category, id=cat_query)
        # if not request.user.is_authenticated and not category.type == Category.TypeChoices.public:
        #     messages.warning(request, 'Para poder acceder a categorias de suscripción o pago debes estar registrado')
        #     return redirect('login')
        contents = contents.filter(category_id=cat_query)
    # Si no se filtra por categoria, verificar si el usuario está logueado, y si no mostrar solo los contenidos de categorias públicas
    # UPDATE: se deja buscar a cualquiera nomas, hasta la previsualizacion
    # TODO: para usuarios logueados, mostrar los contenidos de categorias de pago a los que están suscriptos
    # else:
    #     if not request.user.is_authenticated:
    #         contents = contents.filter(category__type=Category.TypeChoices.public)

    # Si ingreso un parámetro de buscar, filtrar con un OR por titulo y nombre del autor
    if query:
        contents = contents.filter(
            Q(title__icontains=query) | Q(autor__name__icontains=query)
        )

    paginator = Paginator(contents, 10)
    str_page_number = request.GET.get('page')
    if str_page_number is None or str_page_number == '':
        page_number = 1
    else:
        page_number = int(str_page_number)
    if (page_number is None) or (page_number < 1): page_number = 1
    page_obj = paginator.get_page(page_number)
    return render(request, 'inicio.html', {'page_obj': page_obj, 'category': category, 'query': query})
