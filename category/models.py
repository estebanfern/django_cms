from django.core.validators import MinValueValidator
from django.db import models

class Category(models.Model):
    """
    Modelo que representa una categoría en la base de datos.

    Define las propiedades básicas de una categoría, como su nombre, descripción,
    estado de actividad y moderación, tipo (pago, público o suscriptor) y lógica
    para manejar precios asociados con categorías de pago.

    :attribute name: Nombre de la categoría, con un máximo de 255 caracteres.
    :type name: CharField
    :attribute description: Descripción breve de la categoría, con un máximo de 255 caracteres.
    :type description: TextField
    :attribute is_active: Indica si la categoría está activa. Por defecto, es True.
    :type is_active: BooleanField
    :attribute is_moderated: Indica si la categoría está moderada. Por defecto, es True.
    :type is_moderated: BooleanField
    :attribute price: Precio asociado a la categoría. Opcional para tipos que no son de pago.
    :type price: PositiveIntegerField
    :attribute stripe_product_id: ID del producto asociado en Stripe.
    :type stripe_product_id: CharField
    :attribute stripe_price_id: ID del precio asociado en Stripe.
    :type stripe_price_id: CharField
    :attribute date_create: Fecha y hora de creación de la categoría.
    :type date_create: DateTimeField
    :attribute type: Tipo de la categoría, con opciones definidas en `TypeChoices`.
    :type type: CharField

    Clases Internas:
        :class TypeChoices: Enumeración de los tipos posibles de categorías.

    Meta:
        :attribute verbose_name: Nombre singular del modelo para mostrar en el panel de administración.
        :type verbose_name: str
        :attribute verbose_name_plural: Nombre plural del modelo para mostrar en el panel de administración.
        :type verbose_name_plural: str
        :attribute db_table: Nombre de la tabla en la base de datos.
        :type db_table: str

    Métodos:
        :method __str__: Retorna una representación en cadena del objeto `Category`.
    """

    name = models.CharField(max_length=255, verbose_name=('Nombre'))
    description = models.TextField(max_length=255, verbose_name=('Descripción'))
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_moderated = models.BooleanField(default=True, verbose_name='Moderado')
    price = models.PositiveIntegerField(
        null=True,        # Permite valores nulos en la base de datos
        blank=True,       # Permite que el campo esté vacío en formularios
        verbose_name=('Costo'),
        validators=[MinValueValidator(7000)]
    )
    stripe_product_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID de Producto en Stripe')
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID de Precio en Stripe')

    date_create= models.DateTimeField(auto_now_add=True, verbose_name=('Fecha de creacion'))

    class TypeChoices(models.TextChoices):
        """
        Enumeración de tipos de categoría utilizando TextChoices.

        Define las opciones disponibles para el campo `type`, permitiendo seleccionar
        entre diferentes tipos predefinidos de categorías.

        :attribute paid: Representa una categoría de pago.
        :type paid: str
        :attribute public: Representa una categoría pública.
        :type public: str
        :attribute suscription: Representa una categoría para suscriptores.
        :type suscription: str
        """

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
        """
        Retorna una representación en cadena del objeto `Category`.

        Devuelve el nombre de la categoría junto con su tipo legible,
        utilizando la descripción de la elección correspondiente.

        :return: Una cadena con el formato "nombre (tipo)".
        :rtype: str
        """

        return f"{self.name} ({self.get_type_display()})"