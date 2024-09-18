from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import app.models


def sendNotification(my_subject, my_message, recipient_list):

    name =  app.models.CustomUser.objects.get(email=recipient_list[0]).first_name
    link_app = "http://localhost:8000"

    context = {
        "name":name,
        "message": my_message,
        "link_app": link_app
    }

    html_message = render_to_string("email/notification.html", context=context)
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject=my_subject,
        body=plain_message,
        from_email=None,
        to=recipient_list
    )

    message.attach_alternative(html_message, "text/html")
    message.send()


def changeState (recipient_list, title, state):

    recipient_list[0] = "fabri11fabian.fr@gmail.com"

    mappState = {
        "draft": "Borrador",
        "revision": "Edicion",
        "to_publish": "A publicar",
        "publish": "Publicado",
        "inactive": "Inactivo"
    }

    state = mappState[state]

    if len(recipient_list) > 1 or recipient_list is None:
        raise ValueError("El destinatario debe ser un único usuario")

    message = "Tu contenido " + title + " ha cambiado de estado a " + state
    sendNotification("Cambio de estado", message, recipient_list)


