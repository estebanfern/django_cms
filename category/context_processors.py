from django.apps import apps


def categories(request):
    """
    Función para obtener y clasificar las categorías de contenido según su tipo.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest

    Lógica:
        - Filtra y clasifica las categorías en tres tipos:
            - 'Publico': Categorías visibles para todos los usuarios.
            - 'Suscriptor': Categorías accesibles solo para usuarios suscriptores.
            - 'Pago': Categorías accesibles solo mediante pago.

    :return: Un diccionario con las categorías clasificadas en:
        - 'categories_publicas': Categorías públicas.
        - 'categories_suscriptores': Categorías para suscriptores.
        - 'categories_pago': Categorías de pago.
    :rtype: dict
    """

    # Obtiene el modelo 'Category' desde el módulo 'category' usando el método 'get_model'
    category_model = apps.get_model('category', 'Category')
    # Retorna un diccionario con las categorías filtradas por tipo
    return {
        'categories_publicas': category_model.objects.filter(type='Publico'),
        'categories_suscriptores': category_model.objects.filter(type='Suscriptor'),
        'categories_pago': category_model.objects.filter(type='Pago'),
    }
