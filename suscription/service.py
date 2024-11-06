import locale
from datetime import datetime

import stripe
from django.http import JsonResponse
from django.utils.timezone import make_aware

from cms.profile import base


def calculate_total_paid(suscription, date_begin_obj, date_end_obj):

    stripe.api_key = base.STRIPE_SECRET_KEY

    total_paid = 0
    try:
        invoices = stripe.Invoice.list(
            subscription=suscription.stripe_subscription_id,
            status='paid'
        )
        for invoice in invoices['data']:
            paid_at = invoice['status_transitions']['paid_at']

            # Convertir Unix timestamp a objetos datetime
            dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))
            formatted_paid_at = dt_paid_at.strftime('%Y-%m-%dT%H:%M')
            date_paid_at = datetime.strptime(formatted_paid_at, '%Y-%m-%dT%H:%M')

            if (not date_begin_obj or date_paid_at >= date_begin_obj) and (
                    not date_end_obj or date_paid_at <= date_end_obj):
                total_paid += invoice['amount_paid']

    except stripe.error.StripeError:
        return JsonResponse("Error en Stripe", status=500)

    return total_paid


def get_last_payment_date(suscription, date_begin_obj, date_end_obj):
    stripe.api_key = base.STRIPE_SECRET_KEY
    try:
        invoices = stripe.Invoice.list(
            subscription=suscription.stripe_subscription_id,
            status='paid'
        )
        for invoice in invoices['data']:
            paid_at = invoice['status_transitions']['paid_at']

            # Convertir Unix timestamp a objetos datetime
            dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))
            formatted_paid_at = dt_paid_at.strftime('%Y-%m-%dT%H:%M')
            date_paid_at = datetime.strptime(formatted_paid_at, '%Y-%m-%dT%H:%M')

            locale.setlocale(locale.LC_TIME, 'es_PY.UTF-8')
            formatted_period_end = dt_paid_at.strftime('%d de %B de %Y a las %H:%M')

            if (not date_begin_obj or date_paid_at >= date_begin_obj) and (
                    not date_end_obj or date_paid_at <= date_end_obj):
                return formatted_period_end

    except stripe.error.StripeError:
        return JsonResponse("Error en Stripe", status=500)


def get_payment_method(suscription):
    stripe.api_key = base.STRIPE_SECRET_KEY
    try:
        # Obtener la ultima factura pagada
        invoices = stripe.Invoice.list(
            subscription=suscription.stripe_subscription_id,
            status='paid',  # Solo facturas pagadas
            limit=1,  # Obtener solo la última factura pagada
        ).data

        if not invoices:
            return "No hay método de pago"

        last_paid_invoice = invoices[0]

        if not last_paid_invoice.get('payment_intent'):
            return "No hay método de pago"

        payment_intent = stripe.PaymentIntent.retrieve(last_paid_invoice['payment_intent'])
        payment_method = stripe.PaymentMethod.retrieve(payment_intent['payment_method'])

        # Verificar si es una tarjeta y retornar detalles
        if payment_method.card:
            return f"{payment_method.card['brand'].capitalize()} •••• {payment_method.card['last4']}"
        else:
            return "No hay método de pago"

    except stripe.error.StripeError as e:
        return JsonResponse("Error en Stripe", status=500)
