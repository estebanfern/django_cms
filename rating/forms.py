from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    """
    Formulario para gestionar la calificación de un contenido.

    Este formulario utiliza un campo de tipo rango para permitir a los usuarios seleccionar una calificación entre 1 y 5.

    :var rating: Campo de calificación, representado como un input tipo rango.
    :type rating: IntegerField

    :Meta:
        model: El modelo asociado con el formulario es el modelo Rating.
        fields: Incluye únicamente el campo 'rating' en el formulario.
    """

    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '1', 'max': '5', 'step': '1'}),
        label='Calificación'
    )

    class Meta:
        model = Rating
        fields = ['rating']
