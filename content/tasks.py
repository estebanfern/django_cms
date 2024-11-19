from celery import shared_task
from django.db.models import Avg
from django.utils import timezone
from content.models import Content
from notification.service import expire_content
from django.db.models import F

@shared_task()
def expire_contents():
    """
    Tarea programada de Celery para expirar contenidos cuya fecha de expiración ha pasado.

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

    :param content_id: ID del contenido cuyo promedio de calificaciones se actualizará.
    :type content_id: int
    """

    content = Content.objects.get(id=content_id)
    avg_rating = content.rating_set.aggregate(Avg('rating'))['rating__avg']
    content.rating_avg = avg_rating or 0.0
    content.save_without_historical_record()

@shared_task()
def update_reactions(content_id):
    """
    Tarea programada de Celery para actualizar la cantidad de likes y dislikes de un contenido.

    :param content_id: ID del contenido cuyas reacciones se actualizarán.
    :type content_id: int
    """

    content = Content.objects.get(id=content_id)
    content.likes_count = content.likes.count() or 0
    content.dislikes_count = content.dislikes.count() or 0
    content.save_without_historical_record()

@shared_task()
def count_view(content_id):
    """
    Tarea de Celery para incrementar el contador de visualizaciones de un contenido.

    :param content_id: ID del contenido cuya visualización se contabilizará.
    :type content_id: int
    """

    Content.objects.filter(id=content_id).update(views_count=F('views_count') + 1)

@shared_task()
def count_share(content_id):
    """
    Tarea de Celery para incrementar el contador de compartidos de un contenido.

    :param content_id: ID del contenido cuyo contador de compartidos se incrementará.
    :type content_id: int
    """

    print(content_id)
    Content.objects.filter(id=content_id).update(shares_count=F('shares_count') + 1)
