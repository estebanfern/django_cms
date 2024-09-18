
from django.utils import timezone
from content.models import Content

def expire_contents():
    contents = Content.objects.filter(
        state=Content.StateChoices.publish,
        date_expire__lt=timezone.now()
    )
    for content in contents:
        content.state = Content.StateChoices.inactive
        content.save()
        #TODO: enviar email al autor para notificar el vencimientu de su contenido

