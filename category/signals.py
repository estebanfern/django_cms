import stripe
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver

from category.models import Category
from cms.profile import base
from suscription.models import Suscription
import notification.service

stripe.api_key = base.STRIPE_SECRET_KEY


@receiver(pre_save, sender=Category)
def cache_previous_category(sender, instance, *args, **kwargs):
    """
    Almacena el estado original de una categoría antes de que se realicen cambios.

    Este método se ejecuta antes de guardar cualquier instancia de `Category`, permitiendo almacenar una copia del estado anterior de la categoría en la propiedad `__original_category` del objeto `instance`.

    :param sender: La clase del modelo que está enviando la señal (`Category` en este caso).
    :type sender: class
    :param instance: La instancia de la categoría que se está guardando.
    :type instance: Category
    :param args: Argumentos posicionales adicionales.
    :type args: list
    :param kwargs: Argumentos con nombre adicionales.
    :type kwargs: dict
    """
    original_category = None
    if instance.id:
        original_category = Category.objects.get(pk=instance.id)

    instance.__original_category = original_category

@receiver(post_save, sender=Category)
def post_save_category_handler(sender, instance, created, **kwargs):
    """
        Maneja eventos después de guardar una instancia de categoría, incluyendo la creación de productos y precios en Stripe y el manejo de suscripciones.

        Este método se ejecuta después de que una instancia de `Category` ha sido guardada. Dependiendo de los cambios realizados (como el cambio de tipo de categoría a pago o el cambio de precio), actualiza la información en Stripe y maneja las suscripciones asociadas.

        - Si la categoría es nueva y de tipo pago, se crea el producto y el precio en Stripe.
        - Si la categoría cambia de tipo a pago, se notifican los cambios y se maneja la actualización en Stripe.
        - Si el precio cambia, se actualiza el precio en Stripe.
        - Si se cambia el estado activo de la categoría, se notifica y se actualiza en Stripe.

        :param sender: La clase del modelo que está enviando la señal (`Category`).
        :type sender: class
        :param instance: La instancia de la categoría que fue guardada.
        :type instance: Category
        :param created: Booleano que indica si la instancia fue creada (True) o actualizada (False).
        :type created: bool
        :param kwargs: Argumentos con nombre adicionales.
        :type kwargs: dict
        """

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
            recurring={"interval": "day"},  # Suscripción mensual
        )

        # Guardar los IDs del producto y precio en el modelo de categoría
        instance.stripe_product_id = product.id
        instance.stripe_price_id = price.id
        instance.save()



    # Si se modifico una categoría
    if instance.__original_category:

        # Si la categoría se cambio de tipo a pago
        if instance.type != instance.__original_category.type and instance.type == Category.TypeChoices.paid:

            notification.service.category_changed_to_paid(instance)

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
                    recurring={"interval": "day"},
                )
                # Guardar los IDs del producto y precio en el modelo de categoría
                instance.stripe_product_id = product.id
                instance.stripe_price_id = price.id
                instance.save()
            else:
                stripe.Product.modify(
                    instance.stripe_product_id,
                    active=instance.is_active,
                    metadata={'category_paid': True},
                )

            list_subscriptions = Suscription.objects.filter(category=instance)
            for subscription in list_subscriptions:
                if subscription.stripe_subscription_id:
                    suscription_stripe = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    if suscription_stripe.status == 'active':
                        subscription.state = Suscription.SuscriptionState.pending_cancellation
                        subscription.save()
                        stripe.Subscription.modify(
                            subscription.stripe_subscription_id,
                            metadata={'category_paid': True}, #  Poner metadata en las suscripciones category_paid = True para que cuando se cancele la suscripcion  en el werbhok se envie notifacion de cancelacion a los usuarios y se cancele la suscripcion en la base de datos
                        )
                    else:
                        subscription.state = Suscription.SuscriptionState.cancelled
                        subscription.save()
                else:
                    if subscription.state == 'active':
                        subscription.state = Suscription.SuscriptionState.cancelled
                        subscription.save()


        # Si la categoría se cambio de pago a tipo a no pago
        if instance.type != instance.__original_category.type and instance.__original_category.type == Category.TypeChoices.paid:

            notification.service.category_changed_to_not_paid(instance)

            stripe.Product.modify(
                instance.stripe_product_id,
                metadata={'category_paid': False},
                active=False,
            )

            list_subscriptions = Suscription.objects.filter(category=instance)
            for subscription in list_subscriptions:
                if subscription.stripe_subscription_id:
                    suscription_stripe = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    if suscription_stripe.status == 'active' and subscription.state != Suscription.SuscriptionState.pending_cancellation:
                        stripe.Subscription.modify(
                            subscription.stripe_subscription_id,
                            cancel_at_period_end=True,
                            metadata={'category_paid': False}, # Poner metadata en las suscripciones category_paid = False para cuando se cancele la suscripcion no se envie notifacion de cancelacion a los usuarios y no se ponga cancelado en la suscripcion en la base de datos
                        )


        # Si se cambio el precio
        if instance.price != instance.__original_category.price and instance.type == Category.TypeChoices.paid:

            if instance.stripe_price_id:
                old_price_stripe = stripe.Price.retrieve(
                    instance.stripe_price_id,
                )
                old_price = old_price_stripe.unit_amount

                if old_price != instance.price:

                    # SI la categoria vieja es una categoria no de pago
                    if not instance.__original_category.price:
                        notification.service.category_price_changed(instance, False)

                    # Desactivar el precio anterior
                    stripe.Price.modify(
                        instance.stripe_price_id,
                        active=False,
                        metadata={'new_price': instance.price},
                    )


        # Si se cambio el estado de la categoría
        if instance.is_active != instance.__original_category.is_active:

            notification.service.category_state_changed(instance)

            # Si la categoría es de pago se modifica en Stripe
            if instance.type == Category.TypeChoices.paid:
                stripe.Product.modify(
                    instance.stripe_product_id,
                    active=instance.is_active,
                )


        # Si se cambio el nombre o la descripción de la categoría
        if instance.name != instance.__original_category.name or instance.description != instance.__original_category.description:

            if instance.name != instance.__original_category.name:
                notification.service.category_name_changed(instance, instance.__original_category.name)

            # Si la categoría existe en stripe se modifica el producto
            if instance.stripe_product_id:
                stripe.Product.modify(
                    instance.stripe_product_id,
                    name=instance.name,
                    description=instance.description,
                )


# Signal para manejar antes de eliminar la categoría
@receiver(pre_delete, sender=Category)
def cache_category_before_delete(sender, instance, *args, **kwargs):
    """
    Almacena una copia de la categoría antes de eliminarla.

    Este método se ejecuta antes de eliminar una instancia de `Category`, permitiendo almacenar una copia del objeto en la propiedad `__pre_delete_category` para su uso en `post_delete`.

    :param sender: La clase del modelo que está enviando la señal (`Category`).
    :type sender: class
    :param instance: La instancia de la categoría que se va a eliminar.
    :type instance: Category
    :param args: Argumentos posicionales adicionales.
    :type args: list
    :param kwargs: Argumentos con nombre adicionales.
    :type kwargs: dict
    """
    instance.__pre_delete_category = Category.objects.get(pk=instance.id)


# Signal para manejar después de eliminar la categoría
@receiver(post_delete, sender=Category)
def handle_category_after_delete(sender, instance, **kwargs):
    """
    Maneja la lógica después de eliminar una categoría, incluyendo la desactivación del producto en Stripe.

    Este método se ejecuta después de que una instancia de `Category` ha sido eliminada. Utiliza la copia de la categoría almacenada en `pre_delete` para realizar las acciones necesarias, como desactivar el producto en Stripe.

    :param sender: La clase del modelo que está enviando la señal (`Category`).
    :type sender: class
    :param instance: La instancia de la categoría que fue eliminada.
    :type instance: Category
    :param kwargs: Argumentos con nombre adicionales.
    :type kwargs: dict
    """
    # Acceder a la copia guardada antes de la eliminación
    original_category = instance.__pre_delete_category

    if original_category.stripe_product_id:
        # Desactivar el producto en Stripe
        stripe.Product.modify(
            original_category.stripe_product_id,
            active=False,
        )
