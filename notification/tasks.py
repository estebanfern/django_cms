import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__) # __name__ será 'notifications'

@shared_task()
def send_notification_task(my_subject, recipient_list ,context, template):

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
