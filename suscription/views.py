import json
import locale
import logging
from io import BytesIO

import openpyxl
from collections import defaultdict
from datetime import datetime

import stripe
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import notification.service
from app.models import CustomUser
from category.models import Category
from suscription.models import Suscription
from django.contrib.auth.decorators import login_required
from cms.profile import base


logger = logging.getLogger(__name__)


# Create your views here.

def my_subscriptions(request):
    user = request.user
    suscriptions = Suscription.objects.filter(user=user)
    for suscription in suscriptions:
        try:
            if suscription.category.type == Category.TypeChoices.paid:
                subscription = stripe.Subscription.retrieve(suscription.stripe_subscription_id)
                date_end = subscription.current_period_end
                date_end_at = make_aware(datetime.fromtimestamp(date_end))
                locale.setlocale(locale.LC_TIME, 'es_PY.UTF-8')
                formatted_period_end = date_end_at.strftime('%d de %B de %Y a las %H:%M')
                suscription.period_end_display = formatted_period_end
        except stripe.error.StripeError as e:
            suscription.period_end_display = "No disponible"
            logger.error(f"Error al obtener la suscripción de Stripe: {e}")

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
    """
    Crea una sesión de pago en Stripe para una categoría de suscripción.

    :param request: Objeto de solicitud HTTP del usuario autenticado.
    :type request: HttpRequest
    :param category_id: ID de la categoría para la cual se crea la sesión de pago.
    :type category_id: int

    :comportamiento:
        - Verifica que la categoría tenga un precio asociado en Stripe.
        - Define el cliente en Stripe con el ID o correo del usuario autenticado.
        - Crea una sesión de pago con la categoría seleccionada, modo de suscripción, URL de éxito y URL de cancelación.

    :return: Objeto de sesión de pago de Stripe o un mensaje de error en caso de excepción.
    :rtype: dict or tuple
    """

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
    """
    Maneja eventos de webhook provenientes de Stripe y realiza acciones según el tipo de evento.

    :param request: Objeto de solicitud HTTP.
    :type request: HttpRequest

    :comportamiento:
        - Verifica la firma del webhook y construye el evento de Stripe.
        - Realiza acciones específicas según el tipo de evento:
          - `checkout.session.completed`: Guarda el ID del cliente de Stripe en el usuario del sistema.
          - `invoice.paid`: Activa o crea una suscripción en la categoría correspondiente.
          - `invoice.payment_failed`: Marca la suscripción como cancelada y notifica el fallo de pago.
          - `customer.subscription.deleted`: Cancela la suscripción en el sistema.
          - `customer.subscription.updated`: Marca la suscripción como pendiente de cancelación.
          - `product.updated`: Desactiva las suscripciones si el producto ha sido desactivado.
          - `price.updated`: Actualiza el precio de la categoría y cancela las suscripciones activas.
          - `customer.created`: Guarda el ID del cliente de Stripe en el usuario del sistema.

    :return: Respuesta JSON indicando el estado de la operación.
    :rtype: JsonResponse
    """

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
                    recurring={"interval": "day"},
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

@login_required
def table_data(request):

    user = request.user
    if not user.has_perm('app.view_finances'):
        suscriptions = Suscription.objects.filter(stripe_subscription_id__isnull=False,category__type=Category.TypeChoices.paid, user=user)
        usr = None
    else:
        suscriptions = Suscription.objects.filter(stripe_subscription_id__isnull=False,category__type=Category.TypeChoices.paid)
        usr = int(request.GET.get('user')) if request.GET.get('user') else None

    cat = int(request.GET.get('category')) if request.GET.get('category') else None
    date_begin = request.GET.get('date_begin') if request.GET.get('date_begin') else None
    date_end = request.GET.get('date_end') if request.GET.get('date_end') else None

    # Aplicar filtros al queryset
    if usr:
        suscriptions = suscriptions.filter(user__id=usr)
    if cat:
        suscriptions = suscriptions.filter(category__id=cat)
    date_begin_obj = make_aware(datetime.strptime(date_begin, '%Y-%m-%dT%H:%M')) if date_begin else None
    date_end_obj = make_aware(datetime.strptime(date_end, '%Y-%m-%dT%H:%M')) if date_end else None

    # Obtener y filtrar las facturas
    invoices_data = []
    total_general = 0
    for suscription in suscriptions:
        try:
            category_id = suscription.category.id
            customer_id = suscription.user.stripe_customer_id
            invoices = stripe.Invoice.list(customer=customer_id, status='paid')

            for invoice in invoices['data']:
                metadata = invoice['subscription_details']['metadata']
                stripe_category_id = metadata.get('category_id')

                if not stripe_category_id or int(stripe_category_id) != category_id:
                    continue

                paid_at = invoice['status_transitions']['paid_at']
                dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))
                locale.setlocale(locale.LC_TIME, 'es_PY.UTF-8')
                formatted_period_end = dt_paid_at.strftime('%d de %B de %Y a las %H:%M')

                if (not date_begin_obj or dt_paid_at >= date_begin_obj) and (not date_end_obj or dt_paid_at <= date_end_obj):
                    total_general += invoice['amount_paid']

                    payment_intent = stripe.PaymentIntent.retrieve(invoice['payment_intent'])
                    payment_method = stripe.PaymentMethod.retrieve(payment_intent['payment_method'])

                    payment_method_details = f"{payment_method.card['brand'].capitalize()} •••• {payment_method.card['last4']}" if payment_method.card else "Otro"

                    invoices_data.append({
                        'fecha_pago': formatted_period_end,
                        'suscriptor': suscription.user.name,
                        'categoria': suscription.category.name,
                        'monto': invoice['amount_paid'],
                        'metodo_pago': payment_method_details,
                    })

        except stripe.error.StripeError:
            return JsonResponse({"error": "Error en Stripe"}, status=500)

    # invoices_data = sorted(invoices_data, key=lambda x: x['fecha_pago'])
    return JsonResponse({'invoices_data': invoices_data, 'total_general': total_general})

@login_required
def finances(request):
    user = request.user
    has_finance_permission = user.has_perm('app.view_finances')
    if not has_finance_permission:
        users = CustomUser.objects.filter(id=user.id)
    else:
        users = CustomUser.objects.all()
    categories = Category.objects.all()
    context = {
        'users': users,
        'categories': categories,
        'has_finance_permission': has_finance_permission,
    }
    return render(request, 'subscription/finance.html', context)

@login_required
def category_totals(request):
    """
    Devuelve el total de compras por categoría en el rango de fechas seleccionado.

    :param request: Objeto de solicitud HTTP.
    :return: JsonResponse con los nombres de categorías y sus totales de compras.
    """

    user = request.user
    if not user.has_perm('app.view_finances'):
        raise PermissionDenied

    # Filtrar por categoría si se seleccionó una
    if request.GET.get('category'):
        category_id = int(request.GET.get('category'))
        suscriptions = Suscription.objects.filter(category_id=category_id, stripe_subscription_id__isnull=False, category__type=Category.TypeChoices.paid)
    else:
        suscriptions = Suscription.objects.filter(stripe_subscription_id__isnull=False, category__type=Category.TypeChoices.paid)

    if request.GET.get('user'):
        user_id = int(request.GET.get('user'))
        suscriptions = suscriptions.filter(user_id=user_id)

    # Filtrar por fechas de suscripción
    if request.GET.get('date_begin'):
        date_begin = request.GET.get('date_begin')
        date_begin_obj = datetime.strptime(date_begin, '%Y-%m-%dT%H:%M')
    else:
        date_begin_obj = None

    if request.GET.get('date_end'):
        date_end = request.GET.get('date_end')
        date_end_obj = datetime.strptime(date_end, '%Y-%m-%dT%H:%M')
    else:
        date_end_obj = None

    category_payment_counts = {}

    for suscription in suscriptions:
        try:
            category_id = suscription.category.id
            customer_id = suscription.user.stripe_customer_id
            invoices = stripe.Invoice.list(customer=customer_id, status='paid')

            for invoice in invoices['data']:
                metadata = invoice['subscription_details']['metadata']
                stripe_category_id = metadata.get('category_id')

                if not stripe_category_id or int(stripe_category_id) != category_id:
                    continue

                paid_at = invoice['status_transitions']['paid_at']

                # Convertir Unix timestamp a objetos datetime
                dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))
                formatted_paid_at = dt_paid_at.strftime('%Y-%m-%dT%H:%M')
                date_paid_at = datetime.strptime(formatted_paid_at, '%Y-%m-%dT%H:%M')

                if (not date_begin_obj or date_paid_at >= date_begin_obj) and (not date_end_obj or date_paid_at <= date_end_obj):
                    category_name = suscription.category.name
                    category_payment_counts[category_name] = category_payment_counts.get(category_name, 0) + 1

        except stripe.error.StripeError as e:
            print(f"Error al obtener facturas de Stripe: {e}")

    # Preparar los datos para el gráfico
    data = {
        'labels': list(category_payment_counts.keys()),
        'totals': list(category_payment_counts.values())
    }

    return JsonResponse(data)


@login_required
def category_timeline(request):

    user = request.user
    if not user.has_perm('app.view_finances'):
        raise PermissionDenied

    # Filtrar suscripciones activas y pagadas
    suscriptions = Suscription.objects.filter(
        stripe_subscription_id__isnull=False,
        category__type=Category.TypeChoices.paid
    )

    # Aplicar filtros del request
    if request.GET.get('category'):
        category_id = int(request.GET.get('category'))
        suscriptions = suscriptions.filter(category_id=category_id)

    if request.GET.get('user'):
        user_id = int(request.GET.get('user'))
        suscriptions = suscriptions.filter(user_id=user_id)

    if request.GET.get('date_begin'):
        date_begin = request.GET.get('date_begin')
        date_begin_obj = datetime.strptime(date_begin, '%Y-%m-%dT%H:%M')
    else:
        date_begin_obj = None

    if request.GET.get('date_end'):
        date_end = request.GET.get('date_end')
        date_end_obj = datetime.strptime(date_end, '%Y-%m-%dT%H:%M')
    else:
        date_end_obj = None

    # Estructura para almacenar la suma diaria por categoría
    category_time_data = defaultdict(lambda: defaultdict(int))  # {categoria: {fecha: total_diario}}

    for suscription in suscriptions:
        try:
            category_id = suscription.category.id
            customer_id = suscription.user.stripe_customer_id
            invoices = stripe.Invoice.list(customer=customer_id, status='paid')

            for invoice in invoices['data']:
                metadata = invoice['subscription_details']['metadata']
                stripe_category_id = metadata.get('category_id')

                if not stripe_category_id or int(stripe_category_id) != category_id:
                    continue

                paid_at = invoice['status_transitions']['paid_at']

                # Convertir Unix timestamp a objetos datetime
                dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))
                formatted_paid_at = dt_paid_at.strftime('%Y-%m-%dT%H:%M')
                date_paid_at = datetime.strptime(formatted_paid_at, '%Y-%m-%dT%H:%M')
                dt_paid_at = dt_paid_at.strftime('%d-%m-%Y')

                if (not date_begin_obj or date_paid_at >= date_begin_obj) and (not date_end_obj or date_paid_at <= date_end_obj):
                    amount_paid = invoice['amount_paid']

                    # Sumar monto a la fecha y categoría correspondiente
                    category_name = suscription.category.name
                    category_time_data[category_name][dt_paid_at] += amount_paid

        except stripe.error.StripeError as e:
            print(f"Error al obtener facturas de Stripe: {e}")

    # Obtener todas las fechas únicas y ordenarlas
    all_dates = sorted({date for dates in category_time_data.values() for date in dates},key=lambda x: datetime.strptime(x, '%d-%m-%Y'))

    # Formatear los datos para que cada categoría tenga datos en todas las fechas
    final_data = {}
    for category, daily_totals in category_time_data.items():
        final_data[category] = {
            'dates': all_dates,
            'amounts': [daily_totals.get(date, 0) for date in all_dates]
        }

    # Construir el JSON de respuesta para Chart.js
    data = {
        'categories': list(final_data.keys()),
        'datasets': [
            {
                'label': category,
                'data': final_data[category]['amounts'],
                'dates': final_data[category]['dates']
            }
            for category in final_data
        ]
    }

    return JsonResponse(data)

@login_required
def daily_totals(request):

    user = request.user
    if not user.has_perm('app.view_finances'):
        raise PermissionDenied

    # Filtrar suscripciones activas y pagadas
    suscriptions = Suscription.objects.filter(
        stripe_subscription_id__isnull=False,
        category__type=Category.TypeChoices.paid
    )

    # Aplicar filtros del request
    if request.GET.get('category'):
        category_id = int(request.GET.get('category'))
        suscriptions = suscriptions.filter(category_id=category_id)

    if request.GET.get('user'):
        user_id = int(request.GET.get('user'))
        suscriptions = suscriptions.filter(user_id=user_id)

    if request.GET.get('date_begin'):
        date_begin = request.GET.get('date_begin')
        date_begin_obj = datetime.strptime(date_begin, '%Y-%m-%dT%H:%M')
    else:
        date_begin_obj = None

    if request.GET.get('date_end'):
        date_end = request.GET.get('date_end')
        date_end_obj = datetime.strptime(date_end, '%Y-%m-%dT%H:%M')
    else:
        date_end_obj = None

    # Diccionario para almacenar los montos diarios
    daily_totals = defaultdict(float)  # {fecha: total_monto}

    # Recorrer cada suscripción y obtener las facturas pagadas
    for suscription in suscriptions:
        try:
            category_id = suscription.category.id
            customer_id = suscription.user.stripe_customer_id
            invoices = stripe.Invoice.list(customer=customer_id, status='paid')

            for invoice in invoices['data']:
                metadata = invoice['subscription_details']['metadata']
                stripe_category_id = metadata.get('category_id')

                if not stripe_category_id or int(stripe_category_id) != category_id:
                    continue

                paid_at = invoice['status_transitions']['paid_at']

                # Convertir Unix timestamp a objetos datetime
                dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))
                formatted_paid_at = dt_paid_at.strftime('%Y-%m-%dT%H:%M')
                date_paid_at = datetime.strptime(formatted_paid_at, '%Y-%m-%dT%H:%M')

                dt_paid_at = dt_paid_at.strftime('%d-%m-%Y')

                if (not date_begin_obj or date_paid_at >= date_begin_obj) and (not date_end_obj or date_paid_at <= date_end_obj):
                    amount_paid = invoice['amount_paid']

                    # Acumular el monto en la fecha correspondiente
                    daily_totals[dt_paid_at] += amount_paid

        except stripe.error.StripeError as e:
            print(f"Error al obtener facturas de Stripe: {e}")

    # Ordenar las fechas
    sorted_dates = sorted(daily_totals.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))

    # Preparar los datos para el gráfico
    data = {
        'dates': sorted_dates,
        'totals': [daily_totals[date] for date in sorted_dates]
    }

    return JsonResponse(data)


@login_required
def export_to_excel(request):

    # Obtener los datos enviados desde el formulario
    invoices_data_json = request.POST.get('invoices_data')
    total_general = request.POST.get('total_general')

    # Convertir los datos JSON a un objeto Python
    invoices_data = json.loads(invoices_data_json)

    if not invoices_data:
        return JsonResponse({"error": "No hay datos para exportar"}, status=400)

    # Crear el archivo Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Suscripciones"

    # Agregar encabezados
    headers = ['Fecha del Pago', 'Suscriptor', 'Categoría', 'Método de Pago', 'Monto']
    ws.append(headers)

    # Agregar los datos de la tabla
    for invoice in invoices_data:
        ws.append([
            invoice['fecha_pago'],
            invoice['suscriptor'],
            invoice['categoria'],
            invoice['metodo_pago'],
            invoice['monto']
        ])

    # Agregar una fila para el total general
    ws.append(["", "", "", "Total General", total_general])

    # Guardar el archivo en un BytesIO en lugar de HttpResponse directamente
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)  # Mover el puntero de archivo al principio

    timestamp = timezone.localtime(timezone.now()).strftime("%d-%m-%Y_%H-%M")

    # Configurar la respuesta HTTP para enviar el archivo
    response = HttpResponse(
        content=excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="finanzas_{timestamp}.xlsx"'

    return response