from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from app.models import CustomUser
from category.models import Category
from taggit.managers import TaggableManager
from django.contrib.auth import get_user_model
from django.db.models import Avg

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
            - inactive: Contenido inactivo.

    Métodos:
        clean: Valida que el estado del contenido sea uno de los definidos en StateChoices.
        save: Sobrescribe el método de guardado para llamar a la validación personalizada antes de guardar.
        __str__: Retorna una representación en cadena del objeto, mostrando su título y estado.
        update_rating_avg: Actualiza el promedio de calificación del contenido.
        get_state_name: Devuelve el nombre descriptivo del estado en español.

    Meta:
        verbose_name (str): Nombre singular del modelo para mostrar en el panel de administración.
        verbose_name_plural (str): Nombre plural del modelo para mostrar en el panel de administración.
        db_table (str): Nombre de la tabla en la base de datos.
    """

    title = models.CharField(max_length=255, verbose_name='Título')
    summary = models.TextField(max_length=255, verbose_name='Resumen')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    autor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Autor')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    date_create= models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    date_expire = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de expiración')
    date_published = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de publicación')
    content = RichTextUploadingField(verbose_name='Contenido')  # Campo de texto enriquecido con CKEditor 5
    tags = TaggableManager()
    history = HistoricalRecords(excluded_fields=['rating_avg', 'likes_count', 'dislikes_count', 'views_count', 'shares_count', 'important'])
    likes = models.ManyToManyField(get_user_model(), related_name='liked_content', blank=True)
    dislikes = models.ManyToManyField(get_user_model(), related_name='disliked_content', blank=True)
    rating_avg = models.FloatField(default = 0.0, verbose_name="Promedio de calificación")
    likes_count = models.IntegerField(default=0, verbose_name="Cantidad de likes")
    dislikes_count = models.IntegerField(default=0, verbose_name="Cantidad de dislikes")
    views_count = models.IntegerField(default=0, verbose_name="Cantidad de visualizaciones")
    shares_count = models.IntegerField(default=0, verbose_name="Cantidad de compartidos")
    important = models.BooleanField(default=False, verbose_name="Destacado")

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
        draft = 'draft', ('Borrador')
        revision = 'revision', ('Revisión')
        to_publish = 'to_publish', ('A publicar')
        publish = 'publish', ('Publicado')
        inactive = 'inactive', ('Inactivo')

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

        :raises ValidationError: Si el estado del contenido no es válido según las opciones definidas en StateChoices.
        """
        # Validar que el estado sea uno de los definidos en StateChoices
        if self.state not in dict(Content.StateChoices.choices):
            raise ValidationError(f"Estado '{self.state}' no es válido.")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para incluir validaciones personalizadas antes de guardar el contenido.
        Este método llama a `clean()` para ejecutar validaciones personalizadas antes de guardar la instancia
        del contenido en la base de datos, asegurando que los datos sean consistentes y válidos.

        :param args: Argumentos posicionales adicionales.
        :param kwargs: Argumentos de palabra clave adicionales.
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

        :return: Una cadena con el formato "título (estado)", donde 'título' es el título del contenido y
        'estado' es la descripción del estado del contenido.
        :rtype: str
        """
        return f"{self.title}"


    def update_rating_avg(self):
        """
        Actualiza el promedio de calificación del contenido.

        Este método recalcula el promedio de todas las calificaciones asociadas al contenido y actualiza
        el campo `rating_avg` en la base de datos.
        """

        avg_rating = self.rating_set.aggregate(Avg('rating'))['rating__avg']
        self.rating_avg = avg_rating or 0.0
        self.save()

    def get_state_name(self, state):
        """
        Devuelve el nombre descriptivo del estado de un contenido en español.

        Si el estado no coincide con ninguna opción, devuelve "Desconocido".

        :param state: El estado del contenido representado por las opciones de `Content.StateChoices`.
        :type state: str
        :return: El nombre descriptivo del estado del contenido en español.
        :rtype: str
        """
        if state == Content.StateChoices.draft:
            return "Borrador"
        elif state == Content.StateChoices.publish:
            return "Publicado"
        elif state == Content.StateChoices.inactive:
            return "Inactivo"
        elif state == Content.StateChoices.to_publish:
            return "A publicar"
        elif state == Content.StateChoices.revision:
            return "Revision"
        else:
            return "Desconocido"
        

class Report(models.Model):
    """
    Representa un reporte de contenido en la plataforma.

    Campos:
        content (ForeignKey): Referencia al contenido reportado.
        reported_by (ForeignKey): Usuario que reportó el contenido. Opcional.
        email (EmailField): Correo electrónico de quien realiza el reporte.
        name (CharField): Nombre de quien realiza el reporte.
        reason (CharField): Motivo del reporte, elegido entre varias opciones predeterminadas.
        description (TextField): Descripción del motivo del reporte.
        created_at (DateTimeField): Fecha y hora en la que se creó el reporte.

    Métodos:
        __str__(): Retorna una representación legible del reporte, indicando el nombre o usuario que reporta y el contenido reportado.
    """

    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Contenido inapropiado'),
        ('abuse', 'Abuso o acoso'),
        ('other', 'Otro'),
    ]

    content = models.ForeignKey(Content, on_delete=models.CASCADE,verbose_name=('Contenido'))
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,verbose_name=('Reportado por'))  # Para que el campo sea opcional
    email = models.EmailField(verbose_name=('Correo Electrónico'))
    name = models.CharField(max_length=255, verbose_name=('Nombre'))
    reason = models.CharField(max_length=50, choices=REASON_CHOICES,verbose_name=('Motivo'))
    description = models.TextField(verbose_name=('Descripción'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=('Fecha de creación'))

    def __str__(self):
        return f"Reporte de {self.email if self.email else self.reported_by} sobre {self.content.title}"