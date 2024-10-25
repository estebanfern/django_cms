import stripe
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from app.models import CustomUser
from cms.profile import base
from suscription.models import Suscription
import notification.service

stripe.api_key = base.STRIPE_SECRET_KEY

@receiver(pre_save, sender=CustomUser)
def cache_previous_user(sender, instance, *args, **kwargs):
    """
    Almacena el estado original de un usuario antes de que se realicen cambios.

    Este método se ejecuta antes de guardar cualquier instancia de `CustomUser`, permitiendo almacenar una copia del estado anterior del usuario en la propiedad `__original_user` del objeto `instance`.

    :param sender: La clase del modelo que está enviando la señal (`CustomUser` en este caso).
    :type sender: class
    :param instance: La instancia del usuario que se está guardando.
    :type instance: CustomUser
    :param args: Argumentos posicionales adicionales.
    :type args: list
    :param kwargs: Argumentos con nombre adicionales.
    :type kwargs: dict
    """
    original_user = None
    if instance.id:
        original_user = CustomUser.objects.get(pk=instance.id)

    instance.__original_user = original_user


@receiver(post_save, sender=CustomUser)
def post_save_user_handler(sender, instance, created, **kwargs):
    """
    Maneja eventos después de guardar una instancia de usuario, incluyendo actualizaciones en Stripe y envío de notificaciones.

    Este método se ejecuta después de que una instancia de `CustomUser` ha sido guardada. Dependiendo de los cambios realizados (como desactivación de la cuenta, cambio de nombre o email), actualiza la información relacionada en Stripe y envía notificaciones correspondientes.

    - Si el usuario fue desactivado, se notificará de la desactivación y se cancelarán las suscripciones en Stripe.
    - Si el nombre fue cambiado, se actualizará en Stripe.
    - Si el email fue cambiado, se notificará el cambio y también se actualizará en Stripe.

    :param sender: La clase del modelo que está enviando la señal (`CustomUser`).
    :type sender: class
    :param instance: La instancia del usuario que fue guardada.
    :type instance: CustomUser
    :param created: Booleano que indica si la instancia fue creada (True) o actualizada (False).
    :type created: bool
    :param kwargs: Argumentos con nombre adicionales.
    :type kwargs: dict
    """

    # Si se modifico un usuario
    if instance.__original_user:
        # Si se desactivo un usuario
        if instance.is_active != instance.__original_user.is_active and not instance.is_active:
            notification.service.user_deactivated(instance)
            # Desactivar todas las suscripciones activas en stripe
            if instance.stripe_customer_id:
                list_subscriptions = Suscription.objects.filter(user=instance, state=Suscription.SuscriptionState.active, stripe_subscription_id__isnull=False)
                for subscription in list_subscriptions:
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True,
                    )

        # Si se cambio el nombre
        if instance.name != instance.__original_user.name:
            # Actualizar el nombre en Stripe
            if instance.stripe_customer_id:
                stripe.Customer.modify(
                    instance.stripe_customer_id,
                    name=instance.name,
                )

        # Si se cambio el email
        if instance.email != instance.__original_user.email:
            notification.service.user_email_changed(instance, instance.__original_user.email)
            # Actualizar el email en Stripe
            if instance.stripe_customer_id:
                stripe.Customer.modify(
                    instance.stripe_customer_id,
                    email=instance.email,
                )

