from django.db.models.signals import post_save
from django.dispatch import receiver

from cms.profile import base
from .models import Suscription
import stripe

stripe.api_key = base.STRIPE_SECRET_KEY

@receiver(post_save, sender=Suscription)
def create_stripe_subscription(sender, instance, created, **kwargs):
    # user = instance.user
    #
    # # Crear cliente en Stripe si no existe
    # if not user.stripe_customer_id:
    #     stripe_customer = stripe.Customer.create(
    #         email=user.email,
    #         name=user.name,
    #     )
    #     user.stripe_customer_id = stripe_customer.id
    #     user.save()  # Guardar el ID del cliente en el usuario
    #
    # # Crear la suscripción en Stripe cuando se crea una suscripción en el sistema
    # if created: #and instance.category_id.Category.TypeChoices.paid:
    #     subscription = stripe.Subscription.create(
    #         customer=user.stripe_customer_id,  # Asegurarse de que el usuario tenga cliente en Stripe
    #         items=[{
    #             'price': instance.category.stripe_price_id,
    #         }],
    #         expand=["latest_invoice.payment_intent"],
    #     )
    #     instance.stripe_subscription_id = subscription.id
    #     instance.save()
    pass