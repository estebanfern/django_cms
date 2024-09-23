from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={'type': 'range', 'min': '1', 'max': '5', 'step': '1'}),
        label='Calificación'
    )

    class Meta:
        model = Rating
        fields = ['rating']
