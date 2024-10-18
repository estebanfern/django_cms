from celery import shared_task
from django.db.models import Avg
from django.utils import timezone
from content.models import Content
from notification.service import expire_content
from django.db.models import F

@shared_task()
def expire_contents():
    """
    Tarea programada de Celery para expirar contenidos publicados cuya fecha de expiración ha pasado.

    Esta función busca todos los contenidos cuyo estado es 'Publicado' y cuya fecha de expiración ha pasado,
    cambiando su estado a 'Inactivo'. Además, se envía una notificación al autor del contenido sobre la expiración.

    Acciones:
        - Filtra los contenidos con estado 'Publicado' cuya fecha de expiración ha pasado.
        - Cambia el estado de los contenidos a 'Inactivo'.
        - Envía una notificación al autor del contenido.

    :return: None
    """
    contents = Content.objects.filter(
        state=Content.StateChoices.publish,
        date_expire__lt=timezone.now()
    )
    for content in contents:
        content.state = Content.StateChoices.inactive
        content.save()
        autor = content.autor
        expire_content(autor,content)


@shared_task()
def update_rating_avg(content_id):
    """
    Tarea programada de Celery para actualizar el promedio de calificaciones de un contenido.

    Esta función calcula el promedio de las calificaciones (`rating`) de un contenido específico y actualiza
    el campo `rating_avg` del modelo de contenido.

    :param content_id: ID del contenido cuyo promedio de calificaciones se actualizará.
    :type content_id: int

    Acciones:
        - Obtiene el contenido por su ID.
        - Calcula el promedio de las calificaciones asociadas.
        - Actualiza el campo `rating_avg` del contenido con el nuevo promedio.

    :return: None
    """
    content = Content.objects.get(id=content_id)
    avg_rating = content.rating_set.aggregate(Avg('rating'))['rating__avg']
    content.rating_avg = avg_rating or 0.0
    content.save_without_historical_record()

@shared_task()
def update_reactions(content_id):
    """
    Tarea programada de Celery para actualizar los likes y dislikes de un contenido.

    Esta función calcula la cantidad de likes y dislikes de un contenido específico y actualiza
    el campo `likes_count` y 'dislikes_count' del modelo de contenido.

    :param content_id: ID del contenido cuyas reaciones se actualizarán.
    :type content_id: int

    Acciones:
        - Obtiene el contenido por su ID.
        - Calcula la cantidad de reacciones.
        - Actualiza los campos del contenido con los nuevos valores..

    :return: None
    """
    content = Content.objects.get(id=content_id)
    content.likes_count = content.likes.count() or 0
    content.dislikes_count = content.dislikes.count() or 0
    content.save_without_historical_record()

@shared_task()
def count_view(content_id):
    Content.objects.filter(id=content_id).update(views_count=F('views_count') + 1)

@shared_task()
def count_share(content_id):
    print(content_id)
    Content.objects.filter(id=content_id).update(shares_count=F('shares_count') + 1)
