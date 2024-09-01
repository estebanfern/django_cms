from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CategoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'
    verbose_name = _("Gestión de Categorías")
