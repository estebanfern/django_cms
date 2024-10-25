from django import template

register = template.Library()

@register.filter
def format_miles(value):
    try:
        value = int(value)
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter
def format_sub_type(value):
    values = {
        'Pago' : 'De Pago',
        'Suscriptor' : 'De suscripción',
        'Publico' : 'Pública',
    }
    return values[value] if value in values else value

@register.filter
def format_sub_state(value):
    values = {
        'active' : 'Activo',
        'cancelled' : 'Cancelado',
        'pending_cancellation' : 'Pendiente de cancelación',
    }
    return values[value] if value in values else value
