from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=('Nombre'))
    description = models.TextField(max_length=255, verbose_name=('Descripción'))
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_moderated = models.BooleanField(default=True, verbose_name='Moderado')
    price = models.DecimalField(max_digits=100, decimal_places=2, verbose_name=('Costo'))
    date_create= models.DateTimeField(auto_now_add=True, verbose_name=('Fecha de creacion'))

    class TypeChoices(models.TextChoices):
        paid = 'Pago', ('Categoría de Pago')
        public = 'Publico', ('Categoría Pública')
        suscription = 'Suscriptor', ('Categoría para Suscriptor')

    type = models.CharField(
            max_length=10,
            choices=TypeChoices.choices,
            default=TypeChoices.paid,
            verbose_name=('Tipo')
        )

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        db_table = 'category'


    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"