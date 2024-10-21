from datetime import datetime


from notification.tasks import send_notification_task
from django.utils.timezone import make_aware

from suscription.models import Suscription


def changeState (recipient_list, content, oldState):
    """
    Cambia el estado de un contenido y notifica a los destinatarios.

    :param recipient_list: Lista de destinatarios a los que se les enviará la notificación.
    :type recipient_list: list
    :param content: Objeto de contenido cuyo estado ha cambiado.
    :type content: Content
    :param oldState: Estado anterior del contenido.
    :type oldState: str

    La función construye un mensaje basado en el estado anterior y el nuevo estado del contenido
    y envía una notificación por correo electrónico a la lista de destinatarios.
    """

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
    """
    Notifica a un usuario sobre cambios en sus roles.

    :param user: Usuario al que se le han añadido o removido roles.
    :type user: User
    :param groups: Lista de grupos (roles) que se le han añadido o removido al usuario.
    :type groups: set
    :param added: Indica si los roles fueron añadidos (True) o removidos (False).
    :type added: bool

    La función envía una notificación por correo al usuario informándole sobre los cambios
    en sus roles dentro de la aplicación.
    """

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
    """
    Envía un correo de bienvenida a un nuevo usuario.

    :param user: Usuario recién registrado en la aplicación.
    :type user: User

    La función envía un correo de bienvenida cuando un usuario se registra por primera vez
    en la aplicación.
    """

    template = "email/notification.html"
    subject = "¡Bienvenido a nuestra aplicación!"

    message = f"¡Hola {user.name}! Gracias por registrarte en nuestra aplicación. Esperamos que disfrutes de tu experiencia."

    context = {
        "message": message,
    }

    send_notification_task.delay(subject, [user.email], context, template)


def expire_content(autor, content):
    """
    Notifica al autor cuando su contenido ha expirado.

    :param autor: Autor del contenido.
    :type autor: User
    :param content: Contenido que ha expirado.
    :type content: Content

    La función envía una notificación al autor cuando el contenido creado por él ha llegado
    a su fecha de expiración.
    """

    template = "email/notification.html"
    subject = "Contenido vencido"
    message = f"Tu contenido {content.title} ha expirado"

    context = {
        "message": message,
    }

    send_notification_task.delay(subject, [autor.email], context, template)

def payment_success(user, category, invoice):
    category_name = category.name
    amount = invoice.amount_paid
    currency = invoice.currency
    period_end = invoice.lines.data[0].period.end
    period_start = invoice.status_transitions.paid_at

    # Convertir Unix timestamp a objetos datetime
    dt_period_end = make_aware(datetime.fromtimestamp(period_end))
    dt_period_start = make_aware(datetime.fromtimestamp(period_start))

    #Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
    formatted_period_end = dt_period_end.strftime('%d/%m/%Y %H:%M:%S' )
    formatted_paid_at = dt_period_start.strftime('%d/%m/%Y %H:%M:%S' )
    template = "email/notification.html"
    subject = "Pago exitoso"
    # TODO: El mensaje debe respetar los saltos de lineas al enviar el correo
    message = f"""
        Nos complace informarte que tu pago por la categoría {category_name} ha sido procesado exitosamente.

        Monto pagado: {amount} {currency}
        Fecha de pago: {formatted_paid_at}
        Próximo pago: {formatted_period_end}

        Gracias por tu confianza en nosotros.
        """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def payment_failed(user, category, invoice):
    category_name = category.name
    amount = invoice.amount_due
    currency = invoice.currency
    period_start = invoice.effective_at

    # Convertir Unix timestamp a objetos datetime
    dt_period_start = make_aware(datetime.fromtimestamp(period_start))

    # Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
    formatted_paid_at = dt_period_start.strftime('%d/%m/%Y %H:%M:%S')

    template = "email/notification.html"
    subject = "Pago fallido"
    # TODO: El mensaje debe respetar los saltos de lineas al enviar el correo
    message = f"""
        Lamentamos informarte que el intento de pago de tu suscripción a la categoría {category_name} por un monto de {amount} {currency} el dia {formatted_paid_at} ha fallado.
    
        Debido a este fallo en el pago, tu suscripción ha sido cancelada automáticamente. Si deseas reactivar tu suscripción, te invitamos a actualizar tu método de pago y suscribirte nuevamente.
    
        Gracias por tu comprensión y lamentamos los inconvenientes.
        """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def subscription_cancelled(user, category):
    category_name = category.name
    template = "email/notification.html"
    subject = "Suscripción cancelada"
    # TODO: El mensaje debe respetar los saltos de lineas al enviar el correo
    message = f"""
    Queremos informarte que tu suscripción a la categoría {category_name} ha sido cancelada satisfactoriamente. A partir de ahora, ya no tendrás acceso a los contenidos de esta categoría.

    Si fue un error o si deseas reactivar tu suscripción en el futuro, puedes volver a suscribirte en cualquier momento a través de nuestro sitio web.
    """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def subscription_pending_cancellation(user, category,subscription):
    category_name = category.name
    current_period_end = subscription.current_period_end

    # Convertir Unix timestamp a objetos datetime
    dt_period_end = make_aware(datetime.fromtimestamp(current_period_end))

    # Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
    formatted_period_end = dt_period_end.strftime('%d/%m/%Y %H:%M:%S')

    template = "email/notification.html"
    subject = "Tu suscripción será cancelada al final del ciclo de facturación"
    # TODO: El mensaje debe respetar los saltos de lineas al enviar el correo
    message = f"""
    Te informamos que tu suscripción a la categoría {category_name} se cancelará automáticamente al final de tu ciclo de facturación actual.
    
    Podrás seguir disfrutando del contenido hasta la fecha de finalización: {formatted_period_end}. Después de esa fecha, perderás el acceso a esta categoría y para volver a disfrutar de los contenidos, deberás suscribirte nuevamente.
    """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def category_changed_to_paid(category):
    template = "email/notification.html"
    subject = f"La categoría {category.name} ahora es de pago"
    list_subscriptions = Suscription.objects.filter(category=category, state=Suscription.SuscriptionState.active)
    for subscription in list_subscriptions:
        user = subscription.user
        # TODO: El mensaje debe respetar los saltos de lineas al enviar el correo
        message = f"""
        Queremos informarte que la categoría {category.name}, a la que estás suscrito, ahora es de pago.

        Para seguir disfrutando del contenido de esta categoría, será necesario que te suscribas con una suscripción de pago..
        """
        context = {
            "message": message,
        }
        send_notification_task.delay(subject, [user.email], context, template)

