import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from app.models import CustomUser
from category.models import Category
from suscription.models import Suscription
from django.contrib.auth.decorators import login_required

# Create your views here.

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

    if suscription and suscription.state != Suscription.SuscriptionState.cancelled:
        return JsonResponse({'status': 'error', 'message': 'Ya estás suscrito a esta categoría'}, status=400)
    
    if category.type == Category.TypeChoices.paid:
        checkout_session = create_checkout_session(request, category_id)
        return JsonResponse({'status': 'success', 'checkout_url': checkout_session.url})
    else:
        suscription = Suscription(user=user, category=category, state='active')
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
            # TODO: Enviar correo de cancelación de suscripción al usuario
            return JsonResponse({'status': 'success', 'message': f'Tu suscripción finalizará al final del ciclo de facturación actual.'})
            # stripe.Subscription.cancel(subscription_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        # suscription.state = Suscription.SuscriptionState.cancelled
        # suscription.save()
    else:
        suscription.state = Suscription.SuscriptionState.cancelled
        suscription.save()

    return JsonResponse({'status': 'success', 'message': f'Te has desuscrito correctamente a la categoría {category.name}'})


@login_required()
def create_checkout_session(request, category_id):

    category = get_object_or_404(Category, id=category_id)

    if not category.stripe_price_id:
        return JsonResponse("La categoría no tiene un precio de Stripe asociado.", 400)

    YOUR_DOMAIN = "http://localhost:8000"

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
                # "billing_cycle_anchor": "now",
            },
            metadata={
                "user_id": request.user.id,
            },
            mode='subscription',
            success_url=YOUR_DOMAIN + '/category/Pago/?stripe_id={CHECKOUT_SESSION_ID}',
            # success_url=YOUR_DOMAIN + '/category/Pago/?paymentSuccess=true',
            cancel_url=YOUR_DOMAIN + '/category/Pago/',
            customer=customer_id,
            customer_email=customer_email,
            saved_payment_method_options={
                "payment_method_save": "enabled"
            },
            # phone_number_collection={
            #     "enabled": False
            # },
            # allow_redisplay="always",
            # payment_method_options={
            #     "card": {
            #         "setup_future_usage": "on_session"
            #     }
            # },
        )
        return checkout_session
    except Exception as e:
        print(e)
        return "Server error", 500


def customer_portal(request):
    YOUR_DOMAIN = "http://localhost:8000"

    customer_id = request.user.stripe_customer_id

    return_url = YOUR_DOMAIN

    portalSession = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = 'whsec_753712c60d4ebc1c92196d5bd7bc92a7c571009f91d0e0f8a24109c542ad2e8d'

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

        customer_id = session.get('customer')  # El cliente se crea automáticamente por Stripe al completar el checkout

        # Solo creamos un cliente en Stripe si el usuario no tiene uno asociado
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


    # Manejar diferentes tipos de eventos
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

            # TODO: Enviar correo de pago exitoso al usuario

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
        customer_email = invoice.get('customer_email')

        try:
            user = CustomUser.objects.get(stripe_customer_id=customer_id)
            category = Category.objects.get(id=category_id)
            suscription = Suscription.objects.filter(user=user, category=category,stripe_subscription_id=subscription_id).first()

            if suscription:
                suscription.state = Suscription.SuscriptionState.cancelled
                stripe.Subscription.cancel(subscription_id)
                suscription.save()

            # TODO: Enviar correo de pago fallido al usuario

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

        if category_paid:
            try:
                customer = stripe.Customer.retrieve(customer_id)
                customer_email = customer.email
                user = CustomUser.objects.get(stripe_customer_id=customer_id)
                category = Category.objects.get(id=category_id)
                suscription = Suscription.objects.filter(user=user, category=category,stripe_subscription_id=subscription_id).first()
                if not suscription:
                    return JsonResponse({'status': 'suscription not found'}, status=404)
                suscription.state = Suscription.SuscriptionState.cancelled
                suscription.save()

                # TODO: Enviar correo de cancelación de suscripción al usuario

            except CustomUser.DoesNotExist:
                return JsonResponse({'status': 'user not found'}, status=404)
            except Category.DoesNotExist:
                return JsonResponse({'status': 'category not found'}, status=404)
            except Suscription.DoesNotExist:
                return JsonResponse({'status': 'suscription not found'}, status=404)

    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        pending_cancellation = subscription['cancel_at_period_end']
        previous_attributes = event['data']['previous_attributes']
        metadata = subscription['metadata']
        category_paid = True

        if "category_paid" in metadata:
            category_paid = metadata["category_paid"]

        #Si se cancela la suscripción al finalizar el periodo de facturación
        if 'cancel_at_period_end' in previous_attributes and pending_cancellation:
            if category_paid:
                subscription_id = subscription['id']
                category_id = subscription["metadata"]["category_id"]
                customer_id = subscription.get('customer')

                try:
                    customer = stripe.Customer.retrieve(customer_id)
                    customer_email = customer.email
                    user = CustomUser.objects.get(stripe_customer_id=customer_id)
                    category = Category.objects.get(id=category_id)
                    suscription = Suscription.objects.filter(user=user, category=category,stripe_subscription_id=subscription_id).first()
                    if not suscription:
                        return JsonResponse({'status': 'suscription not found'}, status=404)
                    suscription.state = Suscription.SuscriptionState.pending_cancellation
                    suscription.save()

                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
                except Category.DoesNotExist:
                    return JsonResponse({'status': 'category not found'}, status=404)
                except Suscription.DoesNotExist:
                    return JsonResponse({'status': 'suscription not found'}, status=404)

            #TODO: Enviar correo de cancelación de suscripción al usuario

    return JsonResponse({'status': 'success'}, status=200)

