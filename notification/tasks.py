import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from content.models import Content
from suscription.models import Suscription

logger = logging.getLogger(__name__) # __name__ será 'notifications'

@shared_task()
def send_notification_task(my_subject, recipient_list ,context, template):
    """
    Envía una notificación por correo electrónico de forma asíncrona.

    :param my_subject: Asunto del correo electrónico.
    :type my_subject: str
    :param recipient_list: Lista de destinatarios del correo.
    :type recipient_list: list
    :param context: Contexto para renderizar el template del correo.
    :type context: dict
    :param template: Ruta del template HTML que será utilizado para el correo.
    :type template: str

    La función genera un mensaje en formato HTML y texto plano, y envía el correo a los destinatarios.
    Si ocurre un error durante el envío, se registra en el logger.
    """

    html_message = render_to_string(template, context=context)
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject=my_subject,
        body=plain_message,
        from_email=None,
        to=recipient_list
    )

    message.attach_alternative(html_message, "text/html")

    try:
        message.send()
    except Exception as e:
        logger.error(f"Error al enviar el correo: {e}")


@shared_task()
def notify_new_content_suscription(content_id):
    """
    Notifica a los usuarios suscritos sobre nuevo contenido en una categoría de su interés.

    :param content_id: ID del contenido que ha sido publicado.
    :type content_id: int

    La función busca todas las suscripciones activas a la categoría del contenido recién publicado
    y envía una notificación a los usuarios suscritos.
    """

    content = Content.objects.get(id=content_id)
    category_id = content.category
    suscriptions = Suscription.objects.filter(category_id=category_id).exclude(state=Suscription.SuscriptionState.cancelled)
    template = "email/notification.html"
    subject = "Nuevo contenido en una categoría de tu interés"
    message = f"Se ha publicado el contenido {content.title} en la categoría {content.category.name} que podría interesarte."
    context = {
        "message": message,
    }
    for suscription in suscriptions:
        send_notification_task.delay(subject, [suscription.user.email], context, template)