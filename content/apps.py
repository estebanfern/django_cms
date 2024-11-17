from django.apps import AppConfig


class ContentConfig(AppConfig):
    """
    Configuración de la aplicación para la gestión de contenidos.

    Define la configuración predeterminada para la aplicación de contenidos, incluyendo el nombre interno
    de la aplicación, el tipo de campo automático por defecto y el nombre descriptivo que se mostrará
    en el panel de administración.

    :attribute default_auto_field: Tipo de campo automático predeterminado para los modelos de la aplicación.
    :type default_auto_field: str
    :attribute name: Nombre interno de la aplicación utilizado por Django.
    :type name: str
    :attribute verbose_name: Nombre descriptivo de la aplicación que se muestra en el panel de administración.
    :type verbose_name: str
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
    verbose_name = ("Gestión de contenidos")

