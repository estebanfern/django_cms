from django.apps import AppConfig


class ContentConfig(AppConfig):
    """
    Configuración de la aplicación para la gestión de contenidos.

    Define la configuración predeterminada para la aplicación de contenidos,
    incluyendo el nombre interno de la aplicación, el tipo de campo automático por defecto
    y el nombre descriptivo que se mostrará en el panel de administración.

    Atributos:
        default_auto_field (str): Especifica el tipo de campo automático predeterminado para los modelos de la aplicación, en este caso, 'BigAutoField'.
        name (str): Nombre interno de la aplicación utilizado por Django, definido como 'content'.
        verbose_name (str): Nombre descriptivo de la aplicación que se muestra en el panel de administración, definido como "Gestión de contenidos".
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
    verbose_name = ("Gestión de contenidos")

