from django.db import models

class Content (models.Model):
    title = models.CharField(max_length=255, verbose_name=('Título'))
    summary = models.TextField(max_length=255, verbose_name=('Resumen'))
    # content = html enriquecido
    # reactions = Reacciones del contenido
    # ratings =  Calificaciones del contenido
    # record = Historial de cambios
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE, verbose_name=('Categoría'))
    autor = models.ForeignKey('app.CustomUser', on_delete=models.CASCADE, verbose_name=('Autor'))
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    date_create= models.DateTimeField(auto_now_add=True, verbose_name=('Fecha de creacion'))
    date_expire = models.DateTimeField(verbose_name=('Fecha de expiración'))

    class StateChoices(models.TextChoices):
        draft = 'Borrador', ('Borrador')
        revision = 'Revisión', ('Revisión')
        to_publish = 'A publicar', ('A publicar')
        publish = 'Publicado', ('Publicado')
        rejected = 'Rechazado', ('Rechazado')

    state = models.CharField(
        choices=StateChoices.choices,
        default=StateChoices.draft,
        verbose_name=('Estado')
    )

    class Meta:
        verbose_name = 'Contenido'
        verbose_name_plural = 'Contenidos'

    def __str__(self):
        return f"{self.title} ({self.get_state_display()})"