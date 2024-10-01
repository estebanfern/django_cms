from django.apps import apps


def suscriptions(request):
    """
    Devuelve las suscripciones activas del usuario autenticado.

    Esta función obtiene las categorías a las que el usuario autenticado está suscrito y las devuelve en un diccionario. Si el usuario no está autenticado, devuelve una lista vacía.

    :param request: El objeto de solicitud HTTP.
    :type request: HttpRequest

    :return: Un diccionario que contiene una lista de las suscripciones activas del usuario, representadas por los IDs de las categorías.
    :rtype: dict
    """

    suscription_model = apps.get_model('suscription', 'Suscription')

    if request.user.is_authenticated:
        user_suscriptions = suscription_model.objects.filter(user=request.user, state='active').values_list('category_id', flat=True)
    else:
        user_suscriptions = []

    # Retorna un diccionario con las categorías filtradas por tipo
    return {
        'user_suscriptions': user_suscriptions
    }
