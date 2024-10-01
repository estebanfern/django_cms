from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from content.tasks import update_rating_avg
from .models import Rating
from content.models import Content
from django.views.decorators.http import require_POST

@require_POST
def rate_content(request, content_id):
    """
    Permite a un usuario autenticado calificar un contenido.

    Este endpoint recibe una solicitud POST para puntuar un contenido. Si el usuario ya ha calificado el contenido previamente, se actualiza la calificación. Además, se actualiza el promedio de calificaciones del contenido.

    :param request: El objeto de solicitud HTTP.
    :type request: HttpRequest
    :param content_id: El ID del contenido que se va a calificar.
    :type content_id: int

    :return: Devuelve una respuesta JSON indicando el estado de la operación.
    :rtype: JsonResponse

    Si el usuario no está autenticado, se devuelve un error 403.
    Si no se proporciona una calificación o el valor es inválido, se devuelve un error 400.
    """

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Para poder puntuar contenidos debes estar registrado'}, status=403)

    content = get_object_or_404(Content, id=content_id)
    user = request.user

    # Obtener el valor del rating enviado
    rating_value = request.POST.get('rating')

    if not rating_value:
        return JsonResponse({'status': 'error', 'message': 'No se proporcionó una calificación'}, status=400)

    try:
        rating_value = int(rating_value)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Valor de calificación no válido'}, status=400)

    # Verificar si el usuario ya ha calificado este contenido
    rating, created = Rating.objects.get_or_create(user=user, content=content)

    # Actualizar la calificación
    rating.rating = rating_value
    rating.save()

    # Actualizar el promedio en el modelo Content
    update_rating_avg.delay(content_id)

    return JsonResponse(
        {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': rating.rating})
