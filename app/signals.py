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
    original_user = None
    if instance.id:
        original_user = CustomUser.objects.get(pk=instance.id)

    instance.__original_user = original_user


@receiver(post_save, sender=CustomUser)
def post_save_user_handler(sender, instance, created, **kwargs):

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
            # TODO: Notificar al usuario que su email fue cambiado
            # Actualizar el email en Stripe
            if instance.stripe_customer_id:
                stripe.Customer.modify(
                    instance.stripe_customer_id,
                    email=instance.email,
                )

