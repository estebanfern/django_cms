from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    """
    Formulario personalizado para el modelo `Category`.

    Este formulario utiliza `ModelForm` para proporcionar una interfaz para crear y editar instancias
    del modelo de categoría. Además, incluye validaciones personalizadas en el metodo `clean` para
    asegurarse de que los datos sean consistentes con las reglas de negocio definidas.

    :attribute Meta: Clase interna que define el modelo y los campos a utilizar en el formulario.
    :type Meta: class
    """

    class Meta:
        model = Category
        fields = ['name', 'description', 'type', 'is_active', 'is_moderated', 'price']

    def clean(self):
        """
        Valida y limpia los datos del formulario de la categoría.

        Este metodo realiza validaciones adicionales más allá de las proporcionadas por el modelo,
        asegurando que los datos cumplen con las reglas específicas de negocio para las categorías.

        :validations:
            - Si el tipo de categoría es 'Pago', verifica que el campo `price` sea obligatorio y tenga un valor positivo.
            - Si el tipo de categoría no es 'Pago', verifica que no se proporcione un valor para `price`.
              En este caso, si se detecta un valor en `price`, se genera un error y el campo se limpia.

        :return: Diccionario con los datos del formulario limpiados y validados.
        :rtype: dict

        :raises ValidationError:
            - Si no se proporciona un precio para una categoría de tipo 'Pago'.
            - Si se proporciona un precio para una categoría que no es de tipo 'Pago'.
        """
        cleaned_data = super().clean()
        tipo = cleaned_data.get('type')
        price = cleaned_data.get('price')

        # Si el tipo es 'Pago', el precio es obligatorio
        if tipo == Category.TypeChoices.paid:
            if not price:
                self.add_error('price', 'El precio es obligatorio para las categorías de pago.')
        else:
            # Si el tipo no es 'Pago', el campo `price` no debe ser obligatorio y debe ser limpiado
            if price is not None and price > 0:
                self.add_error('price', 'No debe ingresar un precio para categorías que no sean de pago.')
                # limpiar el campo price para evitar que se envíe un valor
                cleaned_data['price'] = None

        return cleaned_data
