import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import notification.service
from app.models import CustomUser
from category.models import Category
from suscription.models import Suscription
from django.contrib.auth.decorators import login_required
from cms.profile import base


# Create your views here.

def my_subscriptions(request):
    user = request.user
    suscriptions = Suscription.objects.filter(user=user)
    return render(request, "subscription/subscriptions.html", {'subscriptions': suscriptions})

def suscribe_category(request, category_id):
    """
    Permite a un usuario autenticado suscribirse a una categoría.

    Este endpoint recibe una solicitud POST para que el usuario se suscriba a una categoría. Si el usuario ya está suscrito, se devuelve un error. Para categorías pagas, se debe implementar una pasarela de pagos.

    :param request: El objeto de solicitud HTTP.
    :type request: HttpRequest
    :param category_id: El ID de la categoría a la que el usuario desea suscribirse.
    :type category_id: int

    :return: Devuelve una respuesta JSON indicando el estado de la suscripción.
    :rtype: JsonResponse

    Si el usuario no está autenticado, se devuelve un error 403.
    Si el usuario ya está suscrito a la categoría, se devuelve un error 400.
    """

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Para poder suscribirte a categorias debes estar registrado'}, status=403)
    
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    suscription = Suscription.objects.filter(user=user, category=category).first()

    if suscription and suscription.state == Suscription.SuscriptionState.active:
        return JsonResponse({'status': 'error', 'message': 'Ya estás suscrito a esta categoría'}, status=400)
    
    if category.type == Category.TypeChoices.paid:
        checkout_session = create_checkout_session(request, category_id)
        return JsonResponse({'status': 'success', 'checkout_url': checkout_session.url})
    else:
        if suscription:
            suscription.state = Suscription.SuscriptionState.active
            suscription.save()
        else:
            suscription = Suscription(user=user, category=category, state=Suscription.SuscriptionState.active)
            suscription.save()

    return JsonResponse({'status': 'success', 'message': f'Te has suscrito correctamente a la categoría {category.name}'})

@require_POST
@login_required
def unsuscribe_category(request, category_id):
    """
    Permite a un usuario autenticado desuscribirse de una categoría.

    Este endpoint recibe una solicitud POST para que el usuario se desuscriba de una categoría a la que está suscrito. Si la suscripción no existe, se devuelve un error.

    :param request: El objeto de solicitud HTTP.
    :type request: HttpRequest
    :param category_id: El ID de la categoría de la cual el usuario desea desuscribirse.
    :type category_id: int

    :return: Devuelve una respuesta JSON indicando el estado de la operación de desuscripción.
    :rtype: JsonResponse

    Si el usuario no está suscrito a la categoría, se devuelve un error 400.
    """

    category = get_object_or_404(Category, id=category_id)
    user = request.user

    suscription = Suscription.objects.filter(user=user, category=category).first()

    if not suscription:
        return JsonResponse({'status': 'error', 'message': 'No estás suscrito a esta categoría'}, status=400)

    if suscription.state != Suscription.SuscriptionState.active:
        return JsonResponse({'status': 'error', 'message': 'No estás suscrito a esta categoría'})

    if category.type == Category.TypeChoices.paid:
        subscription_id = suscription.stripe_subscription_id
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True,
            )
            suscription.state = Suscription.SuscriptionState.pending_cancellation
            suscription.save()
            return JsonResponse({'status': 'success', 'message': f'Tu suscripción finalizará al final del ciclo de facturación actual.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        Suscription.objects.filter(user=user, category=category).delete()

    return JsonResponse({'status': 'success', 'message': f'Te has desuscrito correctamente a la categoría {category.name}'})


@login_required()
def create_checkout_session(request, category_id):

    category = get_object_or_404(Category, id=category_id)

    if not category.stripe_price_id:
        return JsonResponse("La categoría no tiene un precio de Stripe asociado.", 400)

    base_url = f"{request.scheme}://{request.get_host()}"

    customer_id = request.user.stripe_customer_id
    customer_email = request.user.email

    if not customer_id:
        customer_id = None
    else:
        customer_email = None

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': category.stripe_price_id,
                    'quantity': 1,
                },
            ],
            subscription_data={
                "metadata": {
                    "category_id": category_id
                },
            },
            metadata={
                "user_id": request.user.id,
            },
            mode='subscription',
            success_url= base_url + '/category/Pago/?stripe_id={CHECKOUT_SESSION_ID}',
            cancel_url= base_url + '/category/Pago/',
            customer=customer_id,
            customer_email=customer_email,
            saved_payment_method_options={
                "payment_method_save": "enabled"
            },
        )
        return checkout_session
    except Exception as e:
        print(e)
        return "Server error", 500

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = base.ENDPOINT_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # El payload no es válido
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # La firma del webhook no es válida
        return JsonResponse({'status': 'invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')

        # Obtener el usuario de la base de datos
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'user not found'}, status=404)

        customer_id = session.get('customer')

        if not user.stripe_customer_id:
            user.stripe_customer_id = customer_id
            user.save()

        # Actualizar el nombre del cliente en Stripe con el nombre del usuario de tu sistema
        try:
            stripe.Customer.modify(
                customer_id,
                name=user.name,  # Nombre del usuario en tu sistema
            )
        except Exception as e:
            return JsonResponse({'status': f'Error al actualizar el cliente en Stripe: {e}'}, status=500)

        invoice_id = session.get('invoice')
        invoice = stripe.Invoice.retrieve(invoice_id)

        payment_intent_id = invoice.get('payment_intent')

        if not payment_intent_id:
            return JsonResponse({'status': 'No se intentó realizar el pago, falta payment_intent'}, status=400)

        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        new_payment_method_id = payment_intent.get('payment_method')
        new_payment_method = stripe.Customer.retrieve_payment_method(customer_id, new_payment_method_id)

        existing_payment_methods = stripe.PaymentMethod.list(
            customer=customer_id,
            type="card",
        )

        count_duplicate = 0
        for payment_method in existing_payment_methods:
            if new_payment_method['card']['fingerprint'] == payment_method['card']['fingerprint'] and new_payment_method['card']['exp_month'] == payment_method['card']['exp_month'] and new_payment_method['card']['exp_year'] == payment_method['card']['exp_year']:
                count_duplicate += 1
            if count_duplicate > 1:
                stripe.PaymentMethod.detach(payment_method['id'])
                count_duplicate -= 1

    if event['type'] == 'invoice.paid':
        invoice = event['data']['object']

        metadata = invoice['subscription_details']['metadata']
        category_id = metadata.get('category_id')

        if not category_id:
            return JsonResponse({'status': 'category_id not found in metadata'}, status=400)

        # Obtener datos de la sesión
        customer_id = invoice.get('customer')
        subscription_id = invoice.get('subscription')
        customer_email = invoice.get('customer_email')

        try:
            user = CustomUser.objects.get(email=customer_email)
            if not user.stripe_customer_id:
                user.stripe_customer_id = customer_id
                user.save()
            category = Category.objects.get(id=category_id)
            suscription = Suscription.objects.filter(user=user, category=category).first()

            if suscription:
                suscription.stripe_subscription_id = subscription_id
                suscription.state = Suscription.SuscriptionState.active
            else:
                suscription = Suscription(user=user, category=category, state=Suscription.SuscriptionState.active, stripe_subscription_id=subscription_id)

            suscription.save()

            notification.service.payment_success(user, category, invoice)

        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'user not found'}, status=404)
        except Category.DoesNotExist:
            return JsonResponse({'status': 'category not found'}, status=404)
        except Suscription.DoesNotExist:
            return JsonResponse({'status': 'suscription not found'}, status=404)

    if event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']

        metadata = invoice['subscription_details']['metadata']
        category_id = metadata.get('category_id')

        if not category_id:
            return JsonResponse({'status': 'category_id not found in metadata'}, status=400)

        # Obtener datos de la sesión
        customer_id = invoice.get('customer')
        subscription_id = invoice.get('subscription')

        try:
            user = CustomUser.objects.get(stripe_customer_id=customer_id)
            category = Category.objects.get(id=category_id)
            suscription = Suscription.objects.filter(user=user, category=category,stripe_subscription_id=subscription_id).first()

            if suscription:
                suscription.state = Suscription.SuscriptionState.cancelled
                stripe.Subscription.cancel(subscription_id)
                suscription.save()
                if suscription.state == Suscription.SuscriptionState.cancelled:
                    notification.service.payment_failed(user, category, invoice, True)
                else:
                    notification.service.payment_failed(user, category, invoice, False)
            else:
                notification.service.payment_failed(user, category, invoice, True)

        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'user not found'}, status=404)
        except Category.DoesNotExist:
            return JsonResponse({'status': 'category not found'}, status=404)
        except Suscription.DoesNotExist:
            return JsonResponse({'status': 'suscription not found'}, status=404)

    if event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription['id']
        category_id = subscription["metadata"]["category_id"]
        customer_id = subscription.get('customer')
        metadata = subscription['metadata']
        category_paid = True

        if "category_paid" in metadata:
            category_paid = metadata["category_paid"]

        if category_paid != 'False':
            try:
                user = CustomUser.objects.get(stripe_customer_id=customer_id)
                category = Category.objects.get(id=category_id)
                suscription = Suscription.objects.filter(user=user, category=category,stripe_subscription_id=subscription_id).first()
                if not suscription:
                    return JsonResponse({'status': 'suscription already deleted'}, status=200)
                suscription.state = Suscription.SuscriptionState.cancelled
                suscription.save()

                notification.service.subscription_cancelled(user, category)

            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'user not found'}, status=404)
            except Category.DoesNotExist:
                return JsonResponse({'status': 'category not found'}, status=404)

    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        pending_cancellation = subscription['cancel_at_period_end']
        previous_attributes = event['data']['previous_attributes']
        metadata = subscription['metadata']
        category_paid = True
        status = subscription['status']

        # Si cambio al estado 'incomplete_expired' se cancela la suscripción sin enviar notificación
        if 'status' in previous_attributes and status != previous_attributes['status'] and status == 'incomplete_expired':
            stripe.Subscription.modify(
                subscription.id,
                category_paid=False,
            )
            stripe.Subscription.delete(subscription.id)

        if "category_paid" in metadata:
            category_paid = metadata["category_paid"]

        #Si se cancela la suscripción al finalizar el periodo de facturación
        if 'cancel_at_period_end' in previous_attributes and pending_cancellation and pending_cancellation != previous_attributes['cancel_at_period_end']:
            if category_paid != 'False':
                subscription_id = subscription['id']
                category_id = subscription["metadata"]["category_id"]
                customer_id = subscription.get('customer')

                try:
                    user = CustomUser.objects.get(stripe_customer_id=customer_id)
                    category = Category.objects.get(id=category_id)
                    suscription = Suscription.objects.filter(user=user, category=category,stripe_subscription_id=subscription_id).first()
                    if not suscription:
                        return JsonResponse({'status': 'suscription not found'}, status=404)
                    suscription.state = Suscription.SuscriptionState.pending_cancellation
                    suscription.save()

                    notification.service.subscription_pending_cancellation(user, category, subscription)

                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
                except Category.DoesNotExist:
                    return JsonResponse({'status': 'category not found'}, status=404)
                except Suscription.DoesNotExist:
                    return JsonResponse({'status': 'suscription not found'}, status=404)

    if event['type'] == 'product.updated':
        product = event['data']['object']
        product_id = product['id']
        previous_attributes = event['data']['previous_attributes']
        active = product['active']
        metadata = product['metadata']
        category_paid = True

        if "category_paid" in metadata:
            category_paid = metadata["category_paid"]

        # Si se desactiva el producto
        if 'active' in previous_attributes and not active and active != previous_attributes['active']:
            if category_paid != 'False':
                try:
                    category = Category.objects.get(stripe_product_id=product_id)
                    list_subscriptions = Suscription.objects.filter(category=category, stripe_subscription_id__isnull=False).exclude(state=Suscription.SuscriptionState.cancelled)
                    for suscription in list_subscriptions:
                        subscription_id = suscription.stripe_subscription_id
                        stripe.Subscription.modify(
                            subscription_id,
                            cancel_at_period_end=True,
                        )
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    if event['type'] == 'price.updated':
        price = event['data']['object']
        price_id = price['id']
        active = price['active']
        metada = price['metadata']

        if 'new_price' in metada:
            new_price = metada['new_price']
        else:
            new_price = None

        # Si se cambia de precio
        if not active and new_price and new_price != price['unit_amount']:
            try:
                category = Category.objects.get(stripe_price_id=price_id)
                # Crear un nuevo precio en Stripe
                new_price_stripe = stripe.Price.create(
                    product=category.stripe_product_id,
                    unit_amount=new_price,
                    currency='PYG',
                    recurring={"interval": "month"},
                )
                # Guardar el nuevo ID del precio en el modelo de categoría
                category.stripe_price_id = new_price_stripe.id
                category.save()

                # Cancelar las suscripciones activas al finalizar el periodo de facturación actual
                list_subscriptions = Suscription.objects.filter(category=category, stripe_subscription_id__isnull=False, state=Suscription.SuscriptionState.active)
                for suscription in list_subscriptions:
                    stripe.Subscription.modify(
                        suscription.stripe_subscription_id,
                        cancel_at_period_end=True,
                    )
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    if event['type'] == 'customer.created':
        customer = event['data']['object']
        customer_id = customer['id']
        email = customer['email']
        user = CustomUser.objects.filter(email=email).first()

        if user:
            if not user.stripe_customer_id:
                user.stripe_customer_id = customer_id
                user.save()
                stripe.Customer.modify(
                    customer_id,
                    name=user.name,
                )


    return JsonResponse({'status': 'success'}, status=200)

