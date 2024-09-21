from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Rating
from content.models import Content
from django.views.decorators.http import require_POST

@login_required
@require_POST
def rate_content(request, content_id):
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

    return JsonResponse(
        {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': rating.rating})
