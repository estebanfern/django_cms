from django.apps import AppConfig

class SuscriptionConfig(AppConfig):
    """
    Configuración de la aplicación de suscripción.

    Define la configuración predeterminada para la aplicación `suscription`, incluyendo el campo
    de clave primaria y el nombre visible en el panel de administración.

    :var default_auto_field: Especifica el tipo de campo predeterminado para claves primarias.
    :type default_auto_field: str
    :var name: Nombre interno de la aplicación dentro del proyecto Django.
    :type name: str
    :var verbose_name: Nombre descriptivo que aparece en el panel de administración.
    :type verbose_name: str
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suscription'
    verbose_name = 'Gestión de Suscripciones'
