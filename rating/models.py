from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from app.models import CustomUser
from content.models import Content


# Create your models here.

class Rating(models.Model):
    """
    Modelo que representa una calificación que un usuario otorga a un contenido.

    :param user: El usuario que realiza la calificación.
    :type user: ForeignKey to CustomUser
    :param content: El contenido al que se le asigna la calificación.
    :type content: ForeignKey to Content
    :param rating: La calificación otorgada, que debe estar entre 1 y 5.
    :type rating: IntegerField
    :param created_at: Fecha y hora en que se creó la calificación.
    :type created_at: DateTimeField

    :Meta:
        unique_together: Define una restricción única para evitar que un usuario califique un contenido más de una vez.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content")
