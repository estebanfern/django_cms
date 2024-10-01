from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from category.models import Category
from suscription.models import Suscription
from django.contrib.auth.decorators import login_required

# Create your views here.

@require_POST
def suscribe_category(request, category_id):
    """
    Permite a un usuario autenticado suscribirse a una categoría.

    Este endpoint recibe una solicitud POST para que el usuario se suscriba a una categoría. Si el usuario ya está suscrito, se devuelve un error. Para categorías pagas, se debe implementar una pasarela de pagos.

    :param request: El objeto de solicitud HTTP.
    :type request: HttpRequest
    :param category_id: El ID de la categoría a la que el usuario desea suscribirse.
    :type category_id: int

    :return: Devuelve una respuesta JSON indicando el estado de la suscripción.
    :rtype: JsonResponse

    Si el usuario no está autenticado, se devuelve un error 403.
    Si el usuario ya está suscrito a la categoría, se devuelve un error 400.
    """

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Para poder suscribirte a categorias debes estar registrado'}, status=403)
    
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    suscription = Suscription.objects.filter(user=user, category=category).first()

    if suscription:
        return JsonResponse({'status': 'error', 'message': 'Ya estás suscrito a esta categoría'}, status=400)
    
    if category.type == Category.TypeChoices.paid:
        #TODO: Implementar pasarela de pagos
        suscription_state = Suscription.SuscriptionState.active
    else:
        suscription_state = Suscription.SuscriptionState.active

    suscription = Suscription(user=user, category=category, state=suscription_state)
    suscription.save()

    return JsonResponse({'status': 'success', 'message': f'Te has suscrito correctamente a la categoría {category.name}'})

@require_POST
@login_required
def unsuscribe_category(request, category_id):
    """
    Permite a un usuario autenticado desuscribirse de una categoría.

    Este endpoint recibe una solicitud POST para que el usuario se desuscriba de una categoría a la que está suscrito. Si la suscripción no existe, se devuelve un error.

    :param request: El objeto de solicitud HTTP.
    :type request: HttpRequest
    :param category_id: El ID de la categoría de la cual el usuario desea desuscribirse.
    :type category_id: int

    :return: Devuelve una respuesta JSON indicando el estado de la operación de desuscripción.
    :rtype: JsonResponse

    Si el usuario no está suscrito a la categoría, se devuelve un error 400.
    """

    category = get_object_or_404(Category, id=category_id)
    user = request.user

    suscription = Suscription.objects.filter(user=user, category=category).first()

    if not suscription:
        return JsonResponse({'status': 'error', 'message': 'No estás suscrito a esta categoría'}, status=400)
    
    if category.type == Category.TypeChoices.paid:
        #TODO: Implementar cancelación de pago automático si lo hubiera
        suscription.delete()
    else:
        suscription.delete()

    return JsonResponse({'status': 'success', 'message': f'Te has desuscrito correctamente a la categoría {category.name}'})
