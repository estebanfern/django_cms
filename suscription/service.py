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
