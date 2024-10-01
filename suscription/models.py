from django.db import models

from app.models import CustomUser
from category.models import Category

class Suscription(models.Model):
    """
    Modelo que representa una suscripción de un usuario a una categoría.

    :param user: El usuario que está suscrito a una categoría.
    :type user: ForeignKey to CustomUser
    :param category: La categoría a la que el usuario está suscrito.
    :type category: ForeignKey to Category
    :param date_subscribed: La fecha en que el usuario se suscribió.
    :type date_subscribed: DateTimeField
    :param state: El estado de la suscripción, que puede ser 'Activo', 'Pendiente de pago' o 'Cancelado'.
    :type state: CharField

    :Meta:
        unique_together: Define una restricción única para evitar que un usuario esté suscrito más de una vez a la misma categoría.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    class SuscriptionState(models.TextChoices):
        active = 'active', ('Activo')
        pending_payment = 'pending_payment', ('Pendiente de pago')
        cancelled = 'cancelled', ('Cancelado')
    state = models.CharField(
        max_length=15,
        choices=SuscriptionState.choices,
        default=SuscriptionState.pending_payment,
        verbose_name=('Tipo')
    )

    class Meta:
        unique_together = ("user", "category")
    