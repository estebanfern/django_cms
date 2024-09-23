from notification.task import send_notification_task


def changeState (recipient_list, content, oldState):

    template = "email/notification.html"
    title = content.title
    newState = content.state

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
        "message": message
    }

    send_notification_task.delay("Cambio de estado", recipient_list, context, template)


def changeRole(user, groups, added):
    template = "email/notification.html"

    # Crear una lista de nombres de grupos
    group_names = ", ".join([group.name for group in groups])

    # Ajustar el asunto dependiendo si los grupos fueron añadidos o removidos
    subject = f"Has sido {'añadido a' if added else 'removido de'} {'varios roles' if len(groups) > 1 else 'un rol'}."

    # Crear el mensaje personalizado según el caso
    message = f"Te informamos que {'se te han asignado' if added else 'se te han removido'} los siguientes roles: {group_names}."

    # Crear el contexto para el template del correo
    context = {
        "message": message,
    }

    # Enviar la notificación al usuario
    send_notification_task.delay(subject, [user.email], context, template)

def welcomeUser(user):
    template = "email/notification.html"
    subject = "¡Bienvenido a nuestra aplicación!"

    message = f"¡Hola {user.name}! Gracias por registrarte en nuestra aplicación. Esperamos que disfrutes de tu experiencia."

    context = {
        "message": message,
    }

    send_notification_task.delay(subject, [user.email], context, template)

