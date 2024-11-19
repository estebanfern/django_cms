from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CategoryConfig(AppConfig):
    """
    Configuración de la aplicación para la gestión de categorías.

    Define la configuración predeterminada para la aplicación de categorías, incluyendo el nombre de la aplicación
    y su nombre visible en el panel de administración.

    :attribute default_auto_field: Tipo de campo automático predeterminado para los modelos de la aplicación.
    :type default_auto_field: str
    :attribute name: Nombre interno de la aplicación utilizado por Django.
    :type name: str
    :attribute verbose_name: Nombre descriptivo de la aplicación que se muestra en el panel de administración.
    :type verbose_name: str
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'
    verbose_name = _("Gestión de Categorías")

    def ready(self):
        """
        Metodo llamado cuando la aplicación está lista.

        Se utiliza para importar las señales asociadas con la aplicación de categorías.

        :return: None
        :rtype: None
        """
        import category.signals
