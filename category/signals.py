import stripe
from django.db.models.signals import post_save
from django.dispatch import receiver

from category.models import Category
from cms.profile import base

stripe.api_key = base.STRIPE_SECRET_KEY

@receiver(post_save, sender=Category)
def create_stripe_product(sender, instance, created, **kwargs):
    if created and instance.type == Category.TypeChoices.paid:
        product = stripe.Product.create(
            name=instance.name,
            description=instance.description,
            active=instance.is_active,
        )

        # Crear el precio del producto en Stripe
        price = stripe.Price.create(
            product=product.id,
            unit_amount=instance.price,  # Stripe maneja los precios en centavos
            currency='PYG',
            recurring={"interval": "month"},  # Suscripción mensual
        )

        # Guardar los IDs del producto y precio en el modelo de categoría
        instance.stripe_product_id = product.id
        instance.stripe_price_id = price.id
        instance.save()