from django import template

register = template.Library()

@register.filter
def format_miles(value):
    """
    Filtro de plantilla para formatear números en formato de miles con puntos como separadores.

    :param value: El valor numérico a formatear.
    :type value: int o str
    :return: El número formateado como un string con puntos como separadores, o el valor original si no es válido.
    :rtype: str
    """
    try:
        value = int(value)
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter
def format_sub_type(value):
    """
    Filtro de plantilla para convertir tipos de suscripción en descripciones amigables.

    :param value: El tipo de suscripción como string.
    :type value: str
    :return: Una descripción más amigable del tipo de suscripción o el valor original si no coincide.
    :rtype: str
    """

    values = {
        'Pago' : 'De Pago',
        'Suscriptor' : 'De suscripción',
        'Publico' : 'Pública',
    }
    return values[value] if value in values else value

@register.filter
def format_sub_state(value):
    """
    Filtro de plantilla para convertir estados de suscripción en descripciones amigables.

    :param value: El estado de la suscripción como string.
    :type value: str
    :return: Una descripción más amigable del estado de la suscripción o el valor original si no coincide.
    :rtype: str
    """

    values = {
        'active' : 'Activo',
        'cancelled' : 'Cancelado',
        'pending_cancellation' : 'Pendiente de cancelación',
    }
    return values[value] if value in values else value
