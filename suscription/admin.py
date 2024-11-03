import locale

import stripe
from django.contrib import admin
from datetime import datetime

from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import make_aware

from category.models import Category
from cms.profile import base
from suscription.models import Suscription
import logging

logger = logging.getLogger(__name__)

class SuscriptionAdmin(admin.ModelAdmin):

    list_display = ('user', 'category','state', 'details')
    list_filter = ('user', 'state', 'category')
    list_display_links = None

    # Campos personalizados que se mostrarán en la vista de detalles
    fields = ('user',
              'category',
              'category_price',
              'state',
              'date_subscribed',
              'billing_period_end',
              'last_payment_date',
              'total_amount_paid',
              'payment_method_details',
              )

    def details(self, obj):
        url = reverse('admin:suscription_suscription_change', args=[obj.pk])
        return format_html('<a href="{}">Ver detalles</a>', url)

    details.short_description = 'Accion'
    details.admin_order_field = 'id'

    def category_price(self, obj):
        """
        Devuelve el precio de la categoría.
        """
        return f"{obj.category.price} PYG"

    category_price.short_description = 'Precio de la Suscripcion'

    def billing_period_end(self, obj):
        stripe.api_key = base.STRIPE_SECRET_KEY
        """
        Devuelve el final del período de facturación de la suscripción, obteniendo la información de Stripe.
        """
        try:
            stripe_subscription = stripe.Subscription.retrieve(obj.stripe_subscription_id)
            current_period_end = stripe_subscription['current_period_end']

            # Convertir Unix timestamp a objetos datetime
            dt_period_end = make_aware(datetime.fromtimestamp(current_period_end))

            locale.setlocale(locale.LC_TIME, 'es_PY.UTF-8')

            formatted_period_end = dt_period_end.strftime('%d de %B de %Y a las %H:%M')

            return formatted_period_end
        except stripe.error.StripeError as e:
            return f"Error al obtener el periodo: {str(e)}"

    billing_period_end.short_description = 'Fecha del FInal del Periodo de Facturación'

    def payment_method_details(self, obj):
        """
        Muestra detalles de la tarjeta en uso para la suscripción.
        """
        stripe.api_key = base.STRIPE_SECRET_KEY
        try:
            if not obj.stripe_subscription_id:
                return "No hay método de pago"

            # Obtener la ultima factura pagada
            invoices = stripe.Invoice.list(
                subscription=obj.stripe_subscription_id,
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
            logger.error(f"Error al obtener el método de pago de Stripe para suscripción {obj.stripe_subscription_id}: {str(e)}")
            return "Error al obtener el método de pago."

    payment_method_details.short_description = "Método de Pago"

    def total_amount_paid(self, obj):
        """
        Calcula el monto total pagado por la suscripción.
        """
        stripe.api_key = base.STRIPE_SECRET_KEY

        try:
            if not obj.stripe_subscription_id:
                return "No hay pagos realizados"

            # Obtener todas las facturas de la suscripción con estado pagado
            invoices = stripe.Invoice.list(subscription=obj.stripe_subscription_id, status="paid")

            # Sumar los montos de cada factura pagada
            total_paid = sum(invoice['amount_paid'] for invoice in invoices)

            return f"{total_paid} {invoices.data[0]['currency'].upper()}" if invoices.data else "No hay pagos realizados"

        except stripe.error.StripeError as e:
            logger.error(f"Error al calcular el total pagado para suscripción {obj.stripe_subscription_id}: {str(e)}")
            return "Error al obtener el monto total pagado."

    total_amount_paid.short_description = "Monto Total Pagado"

    def last_payment_date(self, obj):
        stripe.api_key = base.STRIPE_SECRET_KEY
        try:
            if not obj.stripe_subscription_id:
                return "No hay pagos registrados"

            invoices = stripe.Invoice.list(
                subscription=obj.stripe_subscription_id,
                limit=1,
                status='paid'
            )

            if not invoices:
                return "No hay pagos registrados"

            last_invoice = invoices['data'][0]
            paid_at = last_invoice['status_transitions']['paid_at']

            # Convertir Unix timestamp a objetos datetime
            dt_paid_at = make_aware(datetime.fromtimestamp(paid_at))

            locale.setlocale(locale.LC_TIME, 'es_PY.UTF-8')
            formatted_paid_at = dt_paid_at.strftime('%d de %B de %Y a las %H:%M')

            return formatted_paid_at

        except stripe.error.StripeError as e:
            logger.error(f"Error al obtener la fecha del último pago para suscripción {obj.stripe_subscription_id}: {str(e)}")
            return "Error al obtener la fecha del último pago."

    last_payment_date.short_description = "Fecha del último pago"

    def get_queryset(self, request):
        """
        Sobreescribe el queryset para mostrar solo las suscripciones donde
        stripe_subscription_id no es nulo y la categoría sea de tipo 'paid'.
        """
        queryset = super().get_queryset(request)
        return queryset.filter(stripe_subscription_id__isnull=False, category__type=Category.TypeChoices.paid)


    def has_add_permission(self, request):

        return False

    def has_delete_permission(self, request, obj=None):

        return False

    def has_view_permission(self, request, obj=None):

        return True

    def has_change_permission(self, request, obj=None):

        return False

    def has_module_permission(self, request):

        return True


admin.site.register(Suscription, SuscriptionAdmin)