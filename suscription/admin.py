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


class SuscriptionAdmin(admin.ModelAdmin):

    list_display = ('user', 'category','state', 'details')
    list_filter = ('user', 'state', 'category')
    list_display_links = None

    # Campos personalizados que se mostrarán en la vista de detalles
    fields = ('user', 'category', 'state', 'category_price', 'date_subscribed' , 'billing_period_end')

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