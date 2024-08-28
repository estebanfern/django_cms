from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password1', 'password2')
        labels = {
            'name': 'Nombre',
            'email': 'Correo Electrónico',
            'password1': 'Contraseña',
            'password2': 'Repetir contraseña',
        }
        help_texts = {
            'username': None,
            'password1': 'Su contraseña debe tener al menos 8 caracteres.',
            'password2': 'Ingrese la misma contraseña que antes, para verificación.',
        }
        error_messages = {
            'password1': {
                'password_too_similar': "Su contraseña no puede ser demasiado similar a su información personal.",
                'password_too_short': "Su contraseña debe contener al menos 8 caracteres.",
                'password_too_common': "Su contraseña no puede ser una contraseña comúnmente utilizada.",
                'password_entirely_numeric': "Su contraseña no puede ser completamente numérica.",
            },
        }

        def __init__(self, *args, **kwargs):
            super(CustomUserCreationForm, self).__init__(*args, **kwargs)
            self.fields['name'].widget.attrs.update({'placeholder': 'Nombre*'})
            self.fields['email'].widget.attrs.update({'placeholder': 'Correo Electrónico*'})
            self.fields['password1'].widget.attrs.update({'placeholder': 'Contraseña*'})
            self.fields['password2'].widget.attrs.update({'placeholder': 'Repetir contraseña*'})

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo Electrónico',
        'id': 'yourUsername',
        'required': True,
    }))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña',
        'id': 'yourPassword',
        'required': True,
    }))
