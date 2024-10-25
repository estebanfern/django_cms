#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Ejecuta tareas administrativas de Django, configurando el entorno y gestionando errores de importación.

    :comportamiento:
        - Configura la variable de entorno `DJANGO_SETTINGS_MODULE` con la ruta de configuración deseada.
        - Intenta importar y ejecutar `execute_from_command_line` desde `django.core.management`.
        - Si Django no está instalado, genera un mensaje de error detallado sobre el fallo de importación.

    :raises ImportError: Si Django no está disponible en el entorno o falta la configuración adecuada.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.profile.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
