from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, get_user_model
from .models import CustomUser
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Las credenciales no son correctas.")
            if not user.is_active:
                raise forms.ValidationError("Esta cuenta está desactivada.")
        return cleaned_data

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
        user = super(ProfileUpdateForm, self).save(commit=False)
        # Actualiza solo si los campos no son nulos y no son cadenas vacías
        if self.cleaned_data.get('name') not in [None, ""]:
            user.name = self.cleaned_data['name']
        if self.cleaned_data.get('about') not in [None, ""]:
            user.about = self.cleaned_data['about']
        if self.cleaned_data.get('photo'):
            user.photo = self.cleaned_data['photo']

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

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        try:
            validate_password(new_password, self.user)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return new_password

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

class CustomUserFormAdmin(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'
        widgets = {
            'groups': FilteredSelectMultiple('groups', is_stacked=False)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminar la opción de agregar nuevos grupos
        self.fields['groups'].widget.can_add_related = False
        self.fields['groups'].widget.can_change_related = False

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo Electrónico',
        'id': 'yourUsername',
        'required': True,
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_model = get_user_model()
        if not user_model.objects.filter(email=email).exists():
            raise ValidationError('No se encontró ningún usuario con este correo electrónico.')
        return email

    def send_password_reset_email(self):
        # Aquí puedes incluir la lógica para enviar el correo electrónico de restablecimiento de contraseña.
        # Normalmente, usarías la función `send_mail` o integraciones con servicios de correo.
        # Esto también puede interactuar con la vista que maneje la lógica de recuperación de contraseñas.
        print("email sended")

class SetPasswordForm(forms.Form):
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

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data
