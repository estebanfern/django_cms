from django.apps import AppConfig

class SuscriptionConfig(AppConfig):
    """
    Configuración de la aplicación de suscripción.

    Esta clase define la configuración predeterminada para la aplicación 'suscription'.

    :var default_auto_field: Especifica el campo predeterminado de clave primaria para los modelos de la aplicación.
    :type default_auto_field: str
    :var name: Nombre de la aplicación de Django.
    :type name: str
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suscription'
