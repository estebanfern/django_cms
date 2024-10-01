
def get_filename(filename, request):
    """
    Convierte el nombre de un archivo a mayúsculas.

    :param filename: El nombre del archivo a modificar.
    :type filename: str
    :param request: La solicitud HTTP recibida (no se utiliza en la lógica de la función).
    :type request: HttpRequest

    :return: El nombre del archivo en mayúsculas.
    :rtype: str
    """

    return filename.upper()
