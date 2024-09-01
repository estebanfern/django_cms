from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'type', 'is_active', 'is_moderated', 'price']

    def clean(self):
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
