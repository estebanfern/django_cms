from datetime import datetime

import stripe

from category.models import Category
from cms.profile import base
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

    message = f"¡Hola {user.name}! 🎉 Te damos la más cálida bienvenida a nuestra comunidad. Estamos emocionados de tenerte con nosotros y esperamos que disfrutes de todo lo que hemos preparado para ti. ¡A disfrutar!"

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
    """
    Envía una notificación de éxito de pago al usuario.

    :param user: El usuario que realizó el pago.
    :type user: CustomUser
    :param category: La categoría asociada al pago.
    :type category: Category
    :param invoice: Detalles de la factura de pago.
    :type invoice: Invoice

    :return: None
    """
    category_name = category.name
    amount = invoice.amount_paid
    currency = invoice.currency
    period_end = invoice.lines.data[0].period.end
    period_start = invoice.status_transitions.paid_at

    # Convertir Unix timestamp a objetos datetime
    dt_period_end = make_aware(datetime.fromtimestamp(period_end))
    dt_period_start = make_aware(datetime.fromtimestamp(period_start))

    #Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
    formatted_period_end = dt_period_end.strftime('%d/%m/%Y a las %H:%M' )
    formatted_paid_at = dt_period_start.strftime('%d/%m/%Y a las %H:%M' )
    template = "email/notification.html"
    subject = "Pago exitoso"
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


def payment_failed(user, category, invoice,first_payment = None):
    """
    Envía una notificación de fallo de pago al usuario.

    :param user: El usuario al que se le notifica el fallo de pago.
    :type user: CustomUser
    :param category: La categoría asociada al intento de pago fallido.
    :type category: Category
    :param invoice: Detalles de la factura fallida.
    :type invoice: Invoice
    :param first_payment: Indica si es el primer pago, opcional.
    :type first_payment: bool, optional

    :return: None
    """

    category_name = category.name
    amount = invoice.amount_due
    currency = invoice.currency
    period_start = invoice.effective_at

    # Convertir Unix timestamp a objetos datetime
    dt_period_start = make_aware(datetime.fromtimestamp(period_start))

    # Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
    formatted_paid_at = dt_period_start.strftime('%d/%m/%Y a las %H:%M')

    template = "email/notification.html"
    subject = "Pago fallido"
    if first_payment:
        message = f"""
            Lamentamos informarte que el intento de pago de tu suscripción a la categoría {category_name} por un monto de {amount} {currency} el dia {formatted_paid_at} ha fallado.

            Te invitamos a actualizar tu método de pago para suscribirte.

            Gracias por tu comprensión y lamentamos los inconvenientes.
            """
    else:
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
    """
    Envía una notificación al usuario de la cancelación de su suscripción.

    :param user: El usuario cuya suscripción ha sido cancelada.
    :type user: CustomUser
    :param category: La categoría de la suscripción cancelada.
    :type category: Category

    :return: None
    """

    category_name = category.name
    template = "email/notification.html"
    subject = "Suscripción cancelada"
    message = f"""
    Queremos informarte que tu suscripción a la categoría {category_name} ha sido cancelada satisfactoriamente. A partir de ahora, ya no tendrás acceso a los contenidos de esta categoría.

    Si fue un error o si deseas reactivar tu suscripción en el futuro, puedes volver a suscribirte en cualquier momento a través de nuestro sitio web.
    """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def subscription_pending_cancellation(user, category,subscription):
    """
    Informa al usuario que su suscripción se cancelará al final del ciclo de facturación.

    :param user: El usuario cuya suscripción será cancelada.
    :type user: CustomUser
    :param category: La categoría de la suscripción.
    :type category: Category
    :param subscription: Suscripción pendiente de cancelación.
    :type subscription: Suscription

    :return: None
    """

    category_name = category.name
    current_period_end = subscription.current_period_end

    # Convertir Unix timestamp a objetos datetime
    dt_period_end = make_aware(datetime.fromtimestamp(current_period_end))

    # Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
    formatted_period_end = dt_period_end.strftime('%d/%m/%Y a las %H:%M')

    template = "email/notification.html"
    subject = "Tu suscripción será cancelada al final del ciclo de facturación"
    message = f"""
    Te informamos que tu suscripción a la categoría {category_name} se cancelará automáticamente al final de tu ciclo de facturación actual.
    
    Podrás seguir disfrutando del contenido hasta la fecha de finalización: {formatted_period_end}. Después de esa fecha, perderás el acceso a esta categoría y para volver a disfrutar de los contenidos, deberás suscribirte nuevamente.
    """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def category_changed_to_paid(category):
    """
    Notifica a los usuarios que la categoría ahora es de pago.

    :param category: La categoría que ha cambiado a ser de pago.
    :type category: Category

    :return: None
    """

    template = "email/notification.html"
    subject = f"La categoría {category.name} ahora es de pago"
    list_subscriptions = Suscription.objects.filter(category=category).exclude(state=Suscription.SuscriptionState.cancelled)
    for subscription in list_subscriptions:
        user = subscription.user
        if subscription.state == Suscription.SuscriptionState.active:
            message = f"""
            Queremos informarte que la categoría {category.name}, a la que estás suscrito, ahora es de pago.
    
            Para seguir disfrutando del contenido de esta categoría, será necesario que te suscribas con una suscripción de pago.
            """
        else:
            message = f"""
            Queremos informarte que la categoría {category.name} ahora es de pago.
            """
        context = {
            "message": message,
        }
        send_notification_task.delay(subject, [user.email], context, template)


def category_changed_to_not_paid(category):
    """
    Notifica a los usuarios que la categoría ha cambiado a gratuita o accesible sin pago.

    :param category: La categoría que ha cambiado su estado de pago.
    :type category: Category

    :return: None
    """

    template = "email/notification.html"
    type = category.type
    typeMapped = {
        "Pago": "de Pago",
        "Publico": "Pública",
        "Suscriptor": "para Suscriptores"
    }
    subject = f"La categoría {category.name} ahora es {typeMapped[type]}"
    list_subscriptions = Suscription.objects.filter(category=category, stripe_subscription_id__isnull=False).exclude(state=Suscription.SuscriptionState.cancelled)
    for subscription in list_subscriptions:
        user = subscription.user
        if subscription.state == Suscription.SuscriptionState.active:
            message = f"""
            Nos complace informarte que la categoría {category.name}, a la que estabas suscrito, ahora es {typeMapped[type]}. 
    
            A partir de este cambio, ya no se te seguirá facturando por esta categoría. Podrás seguir disfrutando de todos sus contenidos sin necesidad de realizar pagos adicionales.
    
            Agradecemos tu apoyo continuo y esperamos que sigas disfrutando de los contenido.
            """
        else:
            message = f"""
            Nos complace informarte que la categoría {category.name} ahora es {typeMapped[type]}.
            """
        context = {
            "message": message,
        }
        send_notification_task.delay(subject, [user.email], context, template)


def category_price_changed(category, old_category_paid=None):
    """
    Notifica a los usuarios que el precio de la categoría ha cambiado.

    :param category: La categoría cuyo precio ha sido actualizado.
    :type category: Category
    :param old_category_paid: Indica si la categoría era paga anteriormente.
    :type old_category_paid: bool, optional

    :return: None
    """

    stripe.api_key = base.STRIPE_SECRET_KEY

    template = "email/notification.html"
    subject = f"El precio de la categoría {category.name} ha cambiado"
    list_subscriptions = Suscription.objects.filter(category=category, stripe_subscription_id__isnull=False).exclude(state=Suscription.SuscriptionState.cancelled)
    new_price = category.price

    if old_category_paid is None:
        old_category_paid = True

    for subscription in list_subscriptions:
        user = subscription.user

        stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
        current_period_end = stripe_subscription.current_period_end

        # Convertir Unix timestamp a objetos datetime
        dt_period_end = make_aware(datetime.fromtimestamp(current_period_end))

        # Conversión horaria (%d/%m/%Y %H:%M:%S %Z)
        formatted_period_end = dt_period_end.strftime('%d/%m/%Y a las %H:%M')

        if old_category_paid and subscription.state == Suscription.SuscriptionState.active:
            message = f"""
            Te informamos que el precio de la categoría {category.name} ha sido actualizado a {new_price} PYS mensuales.
    
            Tu suscripción actual continuará activa hasta el {formatted_period_end}, fecha en la cual se cancelará automáticamente. Hasta ese momento, seguirás disfrutando de todos los beneficios de esta categoría.
    
            Si deseas continuar accediendo al contenido de {category.name} después de esa fecha, podrás suscribirte nuevamente con el nuevo precio.
            """
        else:
            message = f"""
            Te informamos que el precio de la categoría {category.name} ha sido actualizado a {new_price} PYS mensuales.
            """
        context = {
            "message": message,
        }
        send_notification_task.delay(subject, [user.email], context, template)


def category_state_changed(category):
    """
    Notifica a los usuarios cuando el estado de la categoría ha cambiado (activada o desactivada).

    :param category: La categoría cuyo estado ha cambiado.
    :type category: Category

    :return: None
    """

    template = "email/notification.html"
    list_subscriptions = Suscription.objects.filter(category=category).exclude(state=Suscription.SuscriptionState.cancelled)

    if category.is_active:
        subject = f"La categoría {category.name} ha sido activada: Acceso habilitado"
        message = f"""
        Nos complace informarte que la categoría {category.name} ha sido activada. A partir de ahora, puedes acceder a todos los contenidos de esta categoría nuevamente.
        """
        for subscription in list_subscriptions:
            user = subscription.user
            context = {
                "message": message,
            }
            send_notification_task.delay(subject, [user.email], context, template)
    else:
        for subscription in list_subscriptions:
            if category.type == Category.TypeChoices.paid and subscription.state == Suscription.SuscriptionState.active:
                subject = f"La categoría {category.name} ha sido desactivada: Acceso suspendido"
                message = f"""
                Queremos informarte que la categoría {category.name} ha sido desactivada y ya no estará disponible para acceder a sus contenidos.

                Tu suscripción será cancelada al final de tu ciclo de facturación actual. A partir de esa fecha, no se te realizará ningún cargo adicional, y no tendrás que pagar más por esta categoría.

                Lamentamos cualquier inconveniente que esto pueda causarte y agradecemos tu confianza en nosotros.
                """
            else:
                subject = f"La categoría {category.name} ha sido desactivada: Acceso suspendido"
                message = f"""
                Queremos informarte que la categoría {category.name} ha sido desactivada. A partir de ahora, ya no podrás acceder a los contenidos de esta categoría.
                """
            user = subscription.user
            context = {
                "message": message,
            }
            send_notification_task.delay(subject, [user.email], context, template)


def category_name_changed(category, old_name):
    """
    Informa a los usuarios que el nombre de la categoría ha cambiado.

    :param category: La categoría cuyo nombre ha cambiado.
    :type category: Category
    :param old_name: El nombre anterior de la categoría.
    :type old_name: str

    :return: None
    """

    template = "email/notification.html"
    subject = f"El nombre de la categoría {old_name} ha sido cambiado"
    list_subscriptions = Suscription.objects.filter(category=category).exclude(state=Suscription.SuscriptionState.cancelled)
    message = f"""
    Te informamos que el nombre de la categoría {old_name} ha sido cambiado a {category.name}.
    """
    for subscription in list_subscriptions:
        user = subscription.user
        context = {
            "message": message,
        }
        send_notification_task.delay(subject, [user.email], context, template)


def user_deactivated(user):
    """
    Envía una notificación al usuario cuando su cuenta ha sido desactivada.

    :param user: El usuario cuya cuenta ha sido desactivada.
    :type user: CustomUser

    :return: None
    """

    template = "email/notification.html"
    subject = "Tu cuenta ha sido desactivada"
    message = f"""
    Lamentamos informarte que tu cuenta ha sido desactivada. A partir de ahora, ya no podrás acceder al sitio web.
    """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)


def user_email_changed(user, old_email):
    """
    Informa al usuario sobre el cambio de su dirección de correo electrónico.

    :param user: El usuario que ha cambiado su dirección de correo.
    :type user: CustomUser
    :param old_email: La dirección de correo electrónico anterior del usuario.
    :type old_email: str

    :return: None
    """

    template = "email/notification.html"
    subject = "Tu dirección de correo electrónico ha sido cambiada"
    message = f"""
    Te informamos que tu dirección de correo electrónico ha sido cambiada de {old_email} a {user.email}.
    """
    context = {
        "message": message,
    }
    send_notification_task.delay(subject, [user.email], context, template)
    send_notification_task.delay(subject, [old_email], context, template)