
def get_filename(filename, request):
    """
    Convierte el nombre de un archivo a mayúsculas.

    Parámetros:
        filename (str): El nombre del archivo a modificar.
        request (HttpRequest): La solicitud HTTP recibida (no se utiliza en la lógica de la función).

    Lógica:
        - Convierte el nombre del archivo proporcionado a letras mayúsculas.

    Retorna:
        str: El nombre del archivo en mayúsculas.
    """

    return filename.upper()
