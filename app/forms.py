from django import forms
from django.conf.global_settings import MEDIA_URL, MEDIA_ROOT
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from cms.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_ENDPOINT_URL, DEFAULT_FILE_STORAGE

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

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            email=self.cleaned_data['email'],
            name=self.cleaned_data['name'],
            password=self.cleaned_data['password1']
        )
        return user

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

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo', 'name', 'about']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # Evita que los campos vacíos sobrescriban datos existentes
        for field in self.fields:
            self.fields[field].required = False

    def save(self, commit=True):
        # print(F'AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID}')
        # print(F'AWS_SECRET_ACCESS_KEY: {AWS_SECRET_ACCESS_KEY}')
        # print(F'AWS_STORAGE_BUCKET_NAME: {AWS_STORAGE_BUCKET_NAME}')
        # print(F'AWS_S3_ENDPOINT_URL: {AWS_S3_ENDPOINT_URL}')
        # print(F'MEDIA_URL: {MEDIA_URL}')
        # print(F'MEDIA_ROOT: {MEDIA_ROOT}')
        # print(F'DEFAULT_FILE_STORAGE: {DEFAULT_FILE_STORAGE}')
        user = super(ProfileUpdateForm, self).save(commit=False)
        # Verifica si los campos están vacíos antes de actualizar
        if not self.cleaned_data.get('name'):
            user.name = self.instance.name
        if not self.cleaned_data.get('about'):
            user.about = self.instance.about
        if not self.cleaned_data.get('photo'):
            user.photo = self.instance.photo

        if commit:
            user.save()

        return user

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña Actual'}),
        required=True
    )
    new_password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva Contraseña'}),
        required=True
    )
    confirm_new_password = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Nueva Contraseña'}),
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not check_password(current_password, self.user.password):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError('Las nuevas contraseñas no coinciden.')

        if check_password(new_password, self.user.password):
            raise forms.ValidationError('La nueva contraseña no puede ser igual a la actual.')

        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user

