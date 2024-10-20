import stripe
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver

from category.models import Category
from cms.profile import base
from suscription.models import Suscription

stripe.api_key = base.STRIPE_SECRET_KEY


@receiver(pre_save, sender=Category)
def cache_previous_category(sender, instance, *args, **kwargs):
    original_category = None
    if instance.id:
        original_category = Category.objects.get(pk=instance.id)

    instance.__original_category = original_category

@receiver(post_save, sender=Category)
def post_save_category_handler(sender, instance, created, **kwargs):

    # Si se creo una categoría de pago
    if created and instance.type == Category.TypeChoices.paid:
        # Crear el producto en Stripe
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

    # Si se modifico una categoría
    if instance.__original_category:
        # Si la categoría se cambio de tipo a pago
        if instance.type != instance.__original_category.type and instance.type == Category.TypeChoices.paid:
            # Si la categoria no tiene un producto en Stripe
            if not instance.stripe_product_id:
                # Crear el producto en Stripe
                product = stripe.Product.create(
                    name=instance.name,
                    description=instance.description,
                    active=instance.is_active,
                )
                # Crear el precio del producto en Stripe
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=instance.price,
                    currency='PYG',
                    recurring={"interval": "month"},
                )
                # Guardar los IDs del producto y precio en el modelo de categoría
                instance.stripe_product_id = product.id
                instance.stripe_price_id = price.id
                instance.save()
            else:
                stripe.Product.modify(
                    instance.stripe_product_id,
                    active=instance.is_active,
                )

            # TODO: Enviar notificación a los suscriptores de la categoría que ahora es de pago si esta activo
            # TODO: Desactivar las suscripciones de los usuarios que no pagaron
            # TODO: Poner metadata en las suscripciones category = paid para cuando se cancele la suscripcion  en el werbhok se envie notifacion de cancelacion a los usuarios y se cancele la suscripcion en la base de datos

            list_subscriptions = stripe.Subscription.list(product=instance.stripe_product_id)
            for subscription in list_subscriptions:
                if subscription.stripe_subscription_id:
                    suscription_stripe = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    if suscription_stripe.status == 'active':
                        subscription.status = Suscription.SuscriptionState.pending_cancellation
                        subscription.save()
                        stripe.Subscription.modify(
                            subscription.stripe_subscription_id,
                            metadata={'category_paid': True},
                        )
                    else:
                        subscription.status = Suscription.SuscriptionState.cancelled
                        subscription.save()
                else:
                    if subscription.status == 'active':
                        subscription.status = Suscription.SuscriptionState.cancelled
                        subscription.save()


        # Si la categoría se cambio de pago a tipo a no pago
        if instance.type != instance.__original_category.type and instance.__original_category.type == Category.TypeChoices.paid:
            stripe.Product.modify(
                instance.stripe_product_id,
                active=False,
            )
            # TODO: Enviar notificación a los suscriptores de la categoría
            # TODO: Activar todas las suscripciones de los usuarios que no esten cancelados
            # TODO: Cancelar las suscripciones de los usuarios en el webhook de Stripe (pending_cancellation)
            # TODO: Poner metadata en las suscripciones category = not_paid para cuando se cancele la suscripcion no se envie notifacion de cancelacion a los usuarios y no se ponga cancelado en la suscripcion en la base de datos

            list_subscriptions = stripe.Subscription.list(product=instance.stripe_product_id)
            for subscription in list_subscriptions:
                if subscription.stripe_subscription_id:
                    suscription_stripe = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    if suscription_stripe.status == 'active' and subscription.status != Suscription.SuscriptionState.pending_cancellation:
                        subscription.status = Suscription.SuscriptionState.active
                        subscription.save()
                        stripe.Subscription.modify(
                            subscription.stripe_subscription_id,
                            cancel_at_period_end=True,
                            metadata={'category_paid': False},
                        )
                else:
                    if subscription.status != Suscription.SuscriptionState.cancelled and subscription.status != Suscription.SuscriptionState.pending_cancellation and subscription.status != Suscription.SuscriptionState.active:
                        subscription.status = Suscription.SuscriptionState.active
                        subscription.save()



        # Si se cambio el precio
        if instance.price != instance.__original_category.price:
            # Si la categoría es de pago se modifica en Stripe
            if instance.type == Category.TypeChoices.paid:
                # Desactivar el precio anterior
                old_proce_stripe = stripe.Price.modify(
                    instance.stripe_price_id,
                    active=False,
                    metadata={'new_price': instance.price},
                )

                # TODO: Migrar las suscripciones a este nuevo precio en el webhook de Stripe y notificar a los usuarios
                # # Crear el precio del producto en Stripe
                # new_price_stripe = stripe.Price.create(
                #     product=instance.stripe_product_id,
                #     unit_amount=instance.price,
                #     currency='PYG',
                #     recurring={"interval": "month"},
                # )
                # # Guardar el nuevo ID del precio en el modelo de categoría
                # instance.stripe_price_id = new_price_stripe.id
                # instance.save()


        # Si se cambio el estado de la categoría
        if instance.is_active != instance.__original_category.is_active:
            # Si la categoría es de pago se modifica en Stripe
            if instance.type == Category.TypeChoices.paid:
                stripe.Product.modify(
                    instance.stripe_product_id,
                    active=instance.is_active,
                )

                # TODO: En el webhook de Stripe, manejar las suscripciones de los usuarios, si se activa o desactiva la categoría
                # if not instance.is_active:
                #     pass
                #     # TODO: Cancelar las suscripciones al finalizar el ciclo actual de facturación en Stripe (pending_cancellation)
                # else:
                #     pass
                #     # TODO: Activar las suscripciones de los usuarios que no esten cancelados


            # TODO: Enviar notificación a los suscriptores de la categoría


        # Si se cambio el nombre o la descripción de la categoría
        if instance.name != instance.__original_category.name or instance.description != instance.__original_category.description:
            # Si la categoría es de pago se modifica en Stripe
            if instance.type == Category.TypeChoices.paid:
                stripe.Product.modify(
                    instance.stripe_product_id,
                    name=instance.name,
                    description=instance.description,
                )
            # TODO: Enviar notificación a los suscriptores de la categoría



# Signal para manejar antes de eliminar la categoría
@receiver(pre_delete, sender=Category)
def cache_category_before_delete(sender, instance, *args, **kwargs):
    """
    Antes de eliminar la categoría, guarda una copia del objeto
    para usarla en el `post_delete`.
    """
    instance.__pre_delete_category = Category.objects.get(pk=instance.id)


# Signal para manejar después de eliminar la categoría
@receiver(post_delete, sender=Category)
def handle_category_after_delete(sender, instance, **kwargs):
    """
    Después de eliminar la categoría, maneja la lógica de Stripe
    utilizando la copia almacenada en `pre_delete`.
    """
    # Acceder a la copia guardada antes de la eliminación
    original_category = instance.__pre_delete_category

    if original_category.stripe_product_id:
        # Desactivar el producto en Stripe
        stripe.Product.modify(
            original_category.stripe_product_id,
            active=False,
        )
        # TODO: En el webhook de Stripe, cancelar las suscripciones de los usuarios (pending_cancellation)
        # if not instance.is_active:
        #     pass
        #     # TODO: Cancelar las suscripciones al finalizar el ciclo actual de facturación en Stripe (pending_cancellation)

        # TODO: Notificar a los suscriptores de la categoría