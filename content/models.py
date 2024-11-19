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

    Define las propiedades y comportamientos asociados a los contenidos creados en la plataforma,
    como su título, estado, categoría, autor, estadísticas y validaciones.

    :attribute title: Título del contenido.
    :type title: CharField
    :attribute summary: Resumen del contenido.
    :type summary: TextField
    :attribute category: Relación con el modelo `Category`.
    :type category: ForeignKey
    :attribute autor: Relación con el modelo `CustomUser`.
    :type autor: ForeignKey
    :attribute is_active: Indica si el contenido está activo.
    :type is_active: BooleanField
    :attribute date_create: Fecha de creación del contenido.
    :type date_create: DateTimeField
    :attribute date_expire: Fecha de expiración del contenido.
    :type date_expire: DateTimeField
    :attribute date_published: Fecha de publicación del contenido.
    :type date_published: DateTimeField
    :attribute content: Texto enriquecido con CKEditor para el contenido principal.
    :type content: RichTextUploadingField
    :attribute tags: Administrador de etiquetas para asociar palabras clave al contenido.
    :type tags: TaggableManager
    :attribute likes: Relación con los usuarios que han dado "me gusta" al contenido.
    :type likes: ManyToManyField
    :attribute dislikes: Relación con los usuarios que han dado "no me gusta" al contenido.
    :type dislikes: ManyToManyField
    :attribute rating_avg: Promedio de calificaciones del contenido.
    :type rating_avg: FloatField
    :attribute likes_count: Cantidad total de "me gusta".
    :type likes_count: IntegerField
    :attribute dislikes_count: Cantidad total de "no me gusta".
    :type dislikes_count: IntegerField
    :attribute views_count: Número total de visualizaciones.
    :type views_count: IntegerField
    :attribute shares_count: Número total de veces que el contenido fue compartido.
    :type shares_count: IntegerField
    :attribute important: Indica si el contenido está marcado como "destacado".
    :type important: BooleanField
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
        Enumeración de estados posibles para un contenido.

        Define las opciones disponibles para el campo `state` del contenido, asegurando que solo se utilicen
        valores predefinidos.

        :attribute draft: Contenido en estado de borrador.
        :type draft: str
        :attribute revision: Contenido en estado de revisión.
        :type revision: str
        :attribute to_publish: Contenido en estado "a publicar".
        :type to_publish: str
        :attribute publish: Contenido publicado.
        :type publish: str
        :attribute inactive: Contenido inactivo.
        :type inactive: str
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
        Valida que el estado del contenido sea uno de los definidos en `StateChoices`.

        :raises ValidationError: Si el estado no pertenece a las opciones válidas.
        """

        # Validar que el estado sea uno de los definidos en StateChoices
        if self.state not in dict(Content.StateChoices.choices):
            raise ValidationError(f"Estado '{self.state}' no es válido.")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el metodo `save` para incluir validaciones personalizadas antes de guardar.

        :param args: Argumentos posicionales adicionales.
        :type args: list
        :param kwargs: Argumentos nombrados adicionales.
        :type kwargs: dict
        """
        self.clean()  # Llama a la validación personalizada
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'
        db_table = 'content'


    def __str__(self):
        """
        Devuelve una representación en cadena del contenido.

        :return: El título del contenido.
        :rtype: str
        """
        return f"{self.title}"


    def update_rating_avg(self):
        """
        Actualiza el promedio de calificación del contenido.

        Calcula el promedio de las calificaciones asociadas al contenido y actualiza el campo `rating_avg`.
        """

        avg_rating = self.rating_set.aggregate(Avg('rating'))['rating__avg']
        self.rating_avg = avg_rating or 0.0
        self.save()

    def get_state_name(self, state):
        """
        Devuelve el nombre descriptivo del estado del contenido en español.

        :param state: Estado del contenido (uno de los valores definidos en `StateChoices`).
        :type state: str
        :return: Nombre descriptivo del estado en español.
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
    Modelo que representa un reporte asociado a un contenido.

    Captura los detalles sobre un reporte realizado por un usuario o visitante,
    incluyendo el motivo y una descripción.

    :attribute content: Contenido reportado.
    :type content: ForeignKey
    :attribute reported_by: Usuario que realizó el reporte. Es opcional.
    :type reported_by: ForeignKey
    :attribute email: Correo electrónico del reportante.
    :type email: EmailField
    :attribute name: Nombre del reportante.
    :type name: CharField
    :attribute reason: Motivo del reporte.
    :type reason: CharField
    :attribute description: Descripción del motivo del reporte.
    :type description: TextField
    :attribute created_at: Fecha de creación del reporte.
    :type created_at: DateTimeField
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
        """
        Devuelve una representación legible del reporte.

        :return: Una cadena que describe el reporte, indicando el reportante y el contenido.
        :rtype: str
        """
        return f"Reporte de {self.email if self.email else self.reported_by} sobre {self.content.title}"