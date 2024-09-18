import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


logger = logging.getLogger(__name__) # __name__ será 'notifications'

def sendNotification(my_subject, recipient_list ,context, template):

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

def changeState (recipient_list, content, oldState):

    template = "email/notification.html"
    link_app = "http://localhost:8000"
    title = content.title
    newState = content.state
    autor = content.autor

    mappState = {
        "draft": "Borrador",
        "revision": "Edicion",
        "to_publish": "A publicar",
        "publish": "Publicado",
        "inactive": "Inactivo"
    }

    mappOldstate = mappState[oldState]
    mappNewstate = mappState[newState]

    message = "Tu contenido " + title + " ha cambiado de estado " + mappOldstate + " a " + mappNewstate

    context = {
        "name": autor,
        "message": message,
        "link_app": link_app
    }

    sendNotification("Cambio de estado", recipient_list, context, template)


def changeRole(user, groups, added):
    template = "email/notification.html"

    # Crear una lista de nombres de grupos
    group_names = ", ".join([group.name for group in groups])

    # Ajustar el asunto dependiendo si los grupos fueron añadidos o removidos
    subject = f"Has sido {'añadido a' if added else 'removido de'} {'varios roles' if len(groups) > 1 else 'un rol'}."

    # Crear el mensaje personalizado según el caso
    message = f"Te informamos que {'se te han asignado' if added else 'se te han removido'} los siguientes roles: {group_names}."

    # Definir el enlace a la aplicación
    link_app = "http://localhost:8000"

    # Crear el contexto para el template del correo
    context = {
        "message": message,
        "link_app": link_app
    }

    # Enviar la notificación al usuario
    sendNotification(subject, [user.email], context, template)


