from django.db import models
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords
from app.models import CustomUser
from category.models import Category


class Content (models.Model):
    """
    Modelo que representa un contenido en la base de datos.

    Este modelo define las propiedades de un contenido, incluyendo su título, resumen, categoría, autor,
    estado de publicación y fechas relevantes. También incluye validaciones personalizadas y opciones
    de estado predefinidas.

    Atributos:
        title (CharField): Título del contenido, con un máximo de 255 caracteres.
        summary (TextField): Resumen del contenido, con un máximo de 255 caracteres.
        category (ForeignKey): Relación con el modelo Category, indicando la categoría del contenido.
        autor (ForeignKey): Relación con el modelo CustomUser, indicando el autor del contenido.
        is_active (BooleanField): Indica si el contenido está activo. Por defecto, es True.
        date_create (DateTimeField): Fecha y hora de creación del contenido, se asigna automáticamente.
        date_expire (DateTimeField): Fecha y hora de expiración del contenido.
        state (CharField): Estado del contenido, con opciones limitadas definidas en `StateChoices`.

    Clases Internas:
        StateChoices (TextChoices): Enumeración de los posibles estados de un contenido:
            - draft: Contenido en borrador.
            - revision: Contenido en revisión.
            - to_publish: Contenido a publicar.
            - publish: Contenido publicado.
            - rejected: Contenido rechazado.

    Métodos:
        clean: Valida que el estado del contenido sea uno de los definidos en StateChoices.
        save: Sobrescribe el método de guardado para llamar a la validación personalizada antes de guardar.
        __str__: Retorna una representación en cadena del objeto, mostrando su título y estado.

    Meta:
        verbose_name (str): Nombre singular del modelo para mostrar en el panel de administración.
        verbose_name_plural (str): Nombre plural del modelo para mostrar en el panel de administración.
        db_table (str): Nombre de la tabla en la base de datos.
    """
    title = models.CharField(max_length=255, verbose_name=('Título'))
    summary = models.TextField(max_length=255, verbose_name=('Resumen'))
    # content = html enriquecido
    # reactions = Reacciones del contenido
    # ratings =  Calificaciones del contenido
    # record = Historial de cambios
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=('Categoría'))
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=('Autor'))
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    date_create= models.DateTimeField(auto_now_add=True, verbose_name=('Fecha de creacion'))
    date_expire = models.DateField(null=True, blank=True,verbose_name=('Fecha de expiración'))
    date_published = models.DateField(null=True, blank=True, verbose_name='Fecha de publicación')
    content = RichTextField(verbose_name='Contenido')  # Campo de texto enriquecido con CKEditor 5
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True, verbose_name='Archivos adjuntos')
    history = HistoricalRecords()

    class StateChoices(models.TextChoices):
        """
        Enumeración de estados posibles para un contenido utilizando TextChoices.

        Define las opciones disponibles para el campo `state` del contenido,
        permitiendo seleccionar entre diferentes estados predefinidos.

        Atributos:
            draft (str): Estado del contenido en borrador.
            revision (str): Estado del contenido en revisión.
            to_publish (str): Estado del contenido a publicar.
            publish (str): Estado del contenido publicado.
            rejected (str): Estado del contenido rechazado.

        Uso:
            Esta enumeración se utiliza para limitar las opciones disponibles en el campo `state` del modelo Content,
            garantizando que solo se seleccionen valores válidos y predefinidos.
        """
        draft = 'Borrador', ('Borrador')
        revision = 'Revisión', ('Revisión')
        to_publish = 'A publicar', ('A publicar')
        publish = 'Publicado', ('Publicado')
        inactive = 'Inactivo', ('Inactivo')

    state = models.CharField(
        choices=StateChoices.choices,
        default=StateChoices.draft,
        max_length=20,
        verbose_name=('Estado')
    )

    def clean(self):
        """
        Valida el estado del contenido asegurando que sea uno de los definidos en StateChoices.

        Este método personaliza la validación del modelo para asegurarse de que el valor del campo `state`
        sea uno de los estados permitidos por la enumeración StateChoices.

        Lanza:
            ValidationError: Si el estado del contenido no es válido según las opciones definidas en StateChoices.
        """
        # Validar que el estado sea uno de los definidos en StateChoices
        if self.state not in dict(Content.StateChoices.choices):
            raise ValidationError(f"Estado '{self.state}' no es válido.")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para incluir validaciones personalizadas antes de guardar el contenido.

        Este método llama a `clean()` para ejecutar validaciones personalizadas antes de guardar la instancia
        del contenido en la base de datos, asegurando que los datos sean consistentes y válidos.

        Parámetros:
            *args: Argumentos posicionales adicionales.
            **kwargs: Argumentos de palabra clave adicionales.
        """
        self.clean()  # Llama a la validación personalizada
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'
        db_table = 'content'


    def __str__(self):
        """
        Retorna una representación en cadena del objeto Content.

        Esta función devuelve el título del contenido junto con su estado legible,
        utilizando la descripción de la elección correspondiente.

        Retorna:
            str: Una cadena con el formato "título (estado)", donde 'título' es el título del contenido y
            'estado' es la descripción del estado del contenido.
        """
        return f"{self.title} ({self.get_state_display()})"
