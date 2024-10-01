from django.apps import AppConfig


class RatingConfig(AppConfig):
    """
    Configuración de la aplicación de rating.

    Esta clase define la configuración predeterminada para la aplicación 'rating'.

    :var default_auto_field: Especifica el campo predeterminado de clave primaria para los modelos de la aplicación.
    :type default_auto_field: str
    :var name: Nombre de la aplicación de Django.
    :type name: str
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rating'
