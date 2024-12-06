from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from category.models import Category
from content.models import Content
from suscription.models import Suscription


# Create your views here.

def home_view(request):
    """
    Vista principal para mostrar contenidos publicados y activos.

    :param request: Solicitud HTTP recibida.
    :type request: HttpRequest

    Lógica:
        - Filtra los contenidos activos, publicados y disponibles antes de la fecha actual.
        - Aplica filtros adicionales según la categoría seleccionada, favoritos del usuario,
          y búsqueda por título o nombre del autor.
        - Divide los contenidos marcados como importantes en grupos de 5.
        - Configura la paginación para mostrar un máximo de 10 contenidos por página.

    :raises Http404: Si no se encuentra la categoría especificada en el filtro.

    :return: Renderiza la plantilla 'inicio.html' con los contenidos filtrados, la información de la categoría,
             la consulta de búsqueda y los contenidos importantes agrupados.
    :rtype: HttpResponse
    """

    cat_query = request.GET.get('cat')
    category = None
    query = request.GET.get('query')
    favs = request.GET.get('favs')
    # Filtra los contenidos activos y publicados, y los ordena por fecha de publicación
    contents = Content.objects.filter(
        is_active=True,
        category__is_active=True,
        state=Content.StateChoices.publish,
        date_published__lt=timezone.now()
    ).select_related('category', 'autor').order_by('-date_published')

    importants = list(divide_in_groups(contents.filter(important__exact=True), 5))

    if request.user.is_authenticated:
        suscribed_categories = Suscription.objects.filter(user=request.user).values_list('category', flat=True)
    else:
        suscribed_categories = []

    if favs:
        contents = contents.filter(category_id__in=suscribed_categories)

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

    # Configura la paginación con un máximo de 10 contenidos por página
    paginator = Paginator(contents, 10)
    str_page_number = request.GET.get('page')
    # Si no se especifica número de página, se establece en la primera página
    if str_page_number is None or str_page_number == '':
        page_number = 1
    else:
        page_number = int(str_page_number)
    if (page_number is None) or (page_number < 1): page_number = 1
    page_obj = paginator.get_page(page_number)

    # Renderiza la plantilla con los contenidos paginados y la información de la categoría y búsqueda
    return render(request, 'inicio.html', {'page_obj': page_obj, 'category': category, 'query': query, 'importants': importants})

def divide_in_groups(lista, tamaño):
    """
    Divide una lista en grupos de un tamaño específico.

    :param lista: La lista que se desea dividir en grupos.
    :type lista: list
    :param tamaño: El tamaño de cada grupo.
    :type tamaño: int
    :return: Un generador que produce sublistas de tamaño especificado.
    :rtype: generator
    """
    for i in range(0, len(lista), tamaño):
        yield lista[i:i + tamaño]
