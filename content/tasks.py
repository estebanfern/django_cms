from celery import shared_task
from django.db.models import Avg
from django.utils import timezone
from content.models import Content
from notification.service import expire_content

@shared_task()
def expire_contents():
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
    content = Content.objects.get(id=content_id)
    avg_rating = content.rating_set.aggregate(Avg('rating'))['rating__avg']
    content.rating_avg = avg_rating or 0.0
    content.save()