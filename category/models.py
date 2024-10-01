from django.db import models

class Category(models.Model):
    """
    Modelo que representa una categoría en la base de datos.

    Este modelo define las propiedades básicas de una categoría, como su nombre, descripción,
    estado de actividad y moderación, y tipo (pago, público o suscriptor). También maneja
    la lógica para los precios asociados con categorías de pago.

    Atributos:
        name (CharField): Nombre de la categoría, con un máximo de 255 caracteres.
        description (TextField): Descripción breve de la categoría, con un máximo de 255 caracteres.
        is_active (BooleanField): Indica si la categoría está activa. Por defecto, es True.
        is_moderated (BooleanField): Indica si la categoría está moderada. Por defecto, es True.
        price (PositiveIntegerField): Precio asociado a la categoría, opcional para tipos que no son de pago.
        date_create (DateTimeField): Fecha y hora de creación de la categoría, se asigna automáticamente.
        type (CharField): Tipo de la categoría, con opciones limitadas definidas en `TypeChoices`.

    Clases Internas:
        TypeChoices (TextChoices): Enumeración de los tipos posibles de categorías:
            - paid: Categoría de Pago.
            - public: Categoría Pública.
            - suscription: Categoría para Suscriptor.

    Meta:
        verbose_name (str): Nombre singular del modelo para mostrar en el panel de administración.
        verbose_name_plural (str): Nombre plural del modelo para mostrar en el panel de administración.
        db_table (str): Nombre de la tabla en la base de datos.

    Métodos:
        __str__: Retorna una representación en cadena del objeto Category.
    """
    name = models.CharField(max_length=255, verbose_name=('Nombre'))
    description = models.TextField(max_length=255, verbose_name=('Descripción'))
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_moderated = models.BooleanField(default=True, verbose_name='Moderado')
    price = models.PositiveIntegerField(
        null=True,        # Permite valores nulos en la base de datos
        blank=True,       # Permite que el campo esté vacío en formularios
        verbose_name=('Costo')
    )
    date_create= models.DateTimeField(auto_now_add=True, verbose_name=('Fecha de creacion'))

    class TypeChoices(models.TextChoices):
        """
        Enumeración de tipos de categoría utilizando TextChoices.

        Define las opciones disponibles para el campo `type` de la categoría,
        permitiendo seleccionar entre diferentes tipos predefinidos de categorías.

        Atributos:
            paid (str): Representa una categoría de pago. Se almacena como 'Pago' en la base de datos y se muestra como 'Categoría de Pago'.
            public (str): Representa una categoría pública. Se almacena como 'Publico' en la base de datos y se muestra como 'Categoría Pública'.
            suscription (str): Representa una categoría para suscriptores. Se almacena como 'Suscriptor' en la base de datos y se muestra como 'Categoría para Suscriptor'.

        Uso:
            Esta enumeración se utiliza para limitar las opciones disponibles en el campo `type` del modelo `Category`,
            garantizando que solo se seleccionen valores válidos y predefinidos.
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
        Retorna una representación en cadena del objeto Category.

        Esta función devuelve el nombre de la categoría junto con su tipo legible,
        utilizando la descripción de la elección correspondiente.

        Retorna:
            str: Una cadena con el formato "nombre (tipo)", donde 'nombre' es el nombre de la categoría y
            'tipo' es la descripción del tipo de la categoría.
        """
        return f"{self.name} ({self.get_type_display()})"