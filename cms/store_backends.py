from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    """
    Clase personalizada para gestionar el almacenamiento de medios públicos en Amazon S3 utilizando S3Boto3Storage.

    Configura las opciones específicas para el almacenamiento de archivos de medios que deben ser accesibles públicamente.

    Atributos:
        :param location: Carpeta base en el bucket S3 donde se almacenan los archivos de medios.
        :type location: str
        :param default_acl: Control de acceso predeterminado para los archivos, configurado como 'public-read' para que los archivos sean accesibles públicamente.
        :type default_acl: str
        :param file_overwrite: Indica si los archivos deben sobrescribirse si ya existen. Está configurado en False para evitar sobrescritura.
        :type file_overwrite: bool

    Propiedades:
        :param querystring_auth: Define si se deben generar URLs firmadas con autenticación para los archivos.
        :type querystring_auth: bool
    """

    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False

    @property
    def querystring_auth(self):
        """
        Propiedad que determina si se deben generar URLs firmadas para los archivos.

        :return: False, indicando que no se generarán URLs firmadas, permitiendo así acceso público sin autenticación.
        :rtype: bool
        """
        return False

class StaticStorage(S3Boto3Storage):
    """
    Clase personalizada para gestionar el almacenamiento de archivos estáticos en Amazon S3 utilizando S3Boto3Storage.

    Configura las opciones específicas para el almacenamiento de archivos estáticos, como CSS y JavaScript, que deben ser accesibles públicamente.

    Atributos:
        :param location: Carpeta base en el bucket S3 donde se almacenan los archivos estáticos.
        :type location: str
        :param default_acl: Control de acceso predeterminado para los archivos, configurado como 'public-read' para que los archivos sean accesibles públicamente.
        :type default_acl: str
    """
    location = 'static'
    default_acl = 'public-read'
