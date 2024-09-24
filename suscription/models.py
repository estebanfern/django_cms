from django.db import models

from app.models import CustomUser
from category.models import Category

class Suscription(models.Model):
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
    