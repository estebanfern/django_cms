from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CategoryConfig(AppConfig):
    """
    Configuración de la aplicación para la gestión de categorías.

    Define la configuración predeterminada para la aplicación de categorías, incluyendo el nombre de la aplicación
    y su nombre visible en el panel de administración.

    Atributos:
        :param default_auto_field: Especifica el tipo de campo automático predeterminado para los modelos de la aplicación.
        :type default_auto_field: str
        :param name: Nombre interno de la aplicación utilizado por Django.
        :type name: str
        :param verbose_name: Nombre descriptivo de la aplicación que se muestra en el panel de administración.
        :type verbose_name: str
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'
    verbose_name = _("Gestión de Categorías")
