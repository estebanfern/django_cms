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
    """
    Formulario personalizado para la creación de usuarios.

    Hereda de:
        UserCreationForm: El formulario base para la creación de usuarios en Django.

    Atributos:
        Meta: Clase interna para definir el modelo y los campos utilizados en el formulario.
    """

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
        """
        Inicializa el formulario y establece los atributos de los campos para mostrar los placeholders personalizados.

        Acciones:
            - Actualiza los atributos de los campos de nombre, correo electrónico, contraseña y repetición de contraseña.
        """

        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Nombre*'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Correo Electrónico*'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Contraseña*'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Repetir contraseña*'})

    def save(self, commit=True):
        """
        Guarda el usuario creado con los datos ingresados en el formulario.

        Parámetros:
            commit (bool): Define si se guarda el usuario inmediatamente en la base de datos.

        Retorna:
            user (CustomUser): El objeto de usuario creado.
        """

        user = CustomUser.objects.create_user(
            email=self.cleaned_data['email'],
            name=self.cleaned_data['name'],
            password=self.cleaned_data['password1']
        )
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado para iniciar sesión con correo electrónico y contraseña.

    Hereda de:
        AuthenticationForm: El formulario base de autenticación en Django.

    Atributos:
        username (EmailField): Campo para ingresar el correo electrónico del usuario.
        password (CharField): Campo para ingresar la contraseña del usuario.
    """

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
        """
        Valida el campo de correo electrónico.

        Acciones:
            - Verifica si el campo de correo electrónico está vacío.

        Lanza:
            ValidationError: Si el correo electrónico no es proporcionado.
        """

        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        return username

    def clean(self):
        """
        Valida el formulario de inicio de sesión.

        Acciones:
            - Autentica al usuario con las credenciales proporcionadas.
            - Verifica si la cuenta del usuario está activa.

        Lanza:
            ValidationError: Si las credenciales no son correctas o si la cuenta está desactivada.

        Retorna:
            dict: Los datos limpios del formulario.
        """

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
    """
    Formulario para actualizar el perfil del usuario.

    Hereda de:
        ModelForm: Formulario base para trabajar con modelos en Django.

    Atributos:
        Meta: Clase interna para definir el modelo y los campos utilizados en el formulario.
    """

    class Meta:
        model = CustomUser
        fields = ['photo', 'name', 'about']

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y establece todos los campos como opcionales.

        Acciones:
            - Actualiza los campos del formulario para que no sean obligatorios.
        """

        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # Evita que los campos vacíos sobrescriban datos existentes
        for field in self.fields:
            self.fields[field].required = False

    def clean_photo(self):
        """
        Valida que el archivo subido para la foto tenga una extensión valida.

        Lanza:
            ValidationError: Si el archivo no tiene una extensión valida.

        Retorna:
            El archivo validado.
        """
        photo = self.cleaned_data.get('photo')
        if photo:
            # Validar el tipo de archivo permitiendo solo .jpg, .jpeg y .png
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if not any(photo.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError('Solo se permiten archivos con extensión .jpg, .jpeg o .png.')
        return photo

    def save(self, commit=True):
        """
        Guarda los cambios en el perfil del usuario.

        Acciones:
            - Actualiza solo los campos que no están vacíos o nulos.
            - Guarda el usuario si `commit` es True.

        Parámetros:
            commit (bool): Define si se guarda el usuario inmediatamente en la base de datos.

        Retorna:
            user (CustomUser): El objeto de usuario actualizado.
        """

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
    """
    Formulario para cambiar la contraseña del usuario.

    Atributos:
        current_password (CharField): Campo para ingresar la contraseña actual del usuario.
        new_password (CharField): Campo para ingresar la nueva contraseña del usuario.
        confirm_new_password (CharField): Campo para confirmar la nueva contraseña del usuario.
    """

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
        """
        Inicializa el formulario con el usuario actual.

        Parámetros:
            user (CustomUser): El usuario que está cambiando la contraseña.
        """

        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        """
        Valida que la contraseña actual proporcionada sea correcta.

        Lanza:
            ValidationError: Si la contraseña actual es incorrecta.

        Retorna:
            str: La contraseña actual validada.
        """

        current_password = self.cleaned_data.get('current_password')
        if not check_password(current_password, self.user.password):
            raise forms.ValidationError('La contraseña actual es incorrecta.')
        return current_password

    def clean_new_password(self):
        """
        Valida la nueva contraseña con las políticas de validación de Django.

        Lanza:
            ValidationError: Si la nueva contraseña no cumple con las políticas de validación.

        Retorna:
            str: La nueva contraseña validada.
        """

        new_password = self.cleaned_data.get('new_password')
        try:
            validate_password(new_password, self.user)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return new_password

    def clean(self):
        """
        Valida el formulario de cambio de contraseña.

        Acciones:
            - Verifica que las nuevas contraseñas coincidan.
            - Verifica que la nueva contraseña no sea igual a la actual.

        Lanza:
            ValidationError: Si las nuevas contraseñas no coinciden o si es igual a la actual.

        Retorna:
            dict: Los datos limpios del formulario.
        """

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
        """
        Guarda la nueva contraseña del usuario.

        Acciones:
            - Establece la nueva contraseña en el usuario.
            - Guarda el usuario si `commit` es True.

        Parámetros:
            commit (bool): Define si se guarda el usuario inmediatamente en la base de datos.

        Retorna:
            user (CustomUser): El usuario con la nueva contraseña.
        """

        new_password = self.cleaned_data['new_password']
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user

class CustomUserFormAdmin(forms.ModelForm):
    """
    Formulario personalizado para la administración de usuarios en el panel de administración de Django.

    Hereda de:
        ModelForm: Formulario base para trabajar con modelos en Django.

    Atributos:
        Meta: Clase interna para definir el modelo y los campos utilizados en el formulario.
        widgets: Define el widget personalizado para el campo de grupos.
    """

    class Meta:
        model = CustomUser
        fields = '__all__'
        widgets = {
            'groups': FilteredSelectMultiple('Roles', is_stacked=False)
        }

    def __init__(self, *args, **kwargs):
        """
        Inicializa el formulario y deshabilita las opciones de agregar o cambiar grupos desde el widget.

        Acciones:
            - Establece que no se puedan agregar o cambiar grupos desde el campo correspondiente.
        """

        super().__init__(*args, **kwargs)
        # Eliminar la opción de agregar nuevos grupos
        self.fields['groups'].widget.can_add_related = False
        self.fields['groups'].widget.can_change_related = False

class PasswordResetForm(forms.Form):
    """
    Formulario para solicitar el restablecimiento de contraseña.

    Atributos:
        email (EmailField): Campo para ingresar el correo electrónico del usuario.
    """

    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo Electrónico',
        'id': 'yourUsername',
        'required': True,
    }))

    def clean_email(self):
        """
        Valida que el correo electrónico proporcionado esté asociado a un usuario existente.

        Lanza:
            ValidationError: Si no se encuentra un usuario con el correo electrónico proporcionado.

        Retorna:
            str: El correo electrónico validado.
        """

        email = self.cleaned_data.get('email')
        user_model = get_user_model()
        if not user_model.objects.filter(email=email).exists():
            raise ValidationError('No se encontró ningún usuario con este correo electrónico.')
        return email

    def send_password_reset_email(self):
        """
        Envía un correo electrónico para restablecer la contraseña.

        Acciones:
            - Implementa la lógica para enviar un correo electrónico de restablecimiento de contraseña.
            - Se puede usar `send_mail` o integraciones con servicios de correo.
        """

        # Aquí puedes incluir la lógica para enviar el correo electrónico de restablecimiento de contraseña.
        # Normalmente, usarías la función `send_mail` o integraciones con servicios de correo.
        # Esto también puede interactuar con la vista que maneje la lógica de recuperación de contraseñas.
        print("email sended")

class SetPasswordForm(forms.Form):
    """
    Formulario para establecer una nueva contraseña.

    Atributos:
        new_password (CharField): Campo para ingresar la nueva contraseña del usuario.
        confirm_new_password (CharField): Campo para confirmar la nueva contraseña del usuario.
    """

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
        """
        Valida la nueva contraseña con las políticas de validación de Django.

        Lanza:
            ValidationError: Si la nueva contraseña no cumple con las políticas de validación.

        Retorna:
            str: La nueva contraseña validada.
        """

        new_password = self.cleaned_data.get('new_password')
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return new_password

    def clean(self):
        """
        Valida que las nuevas contraseñas coincidan.

        Lanza:
            ValidationError: Si las contraseñas no coinciden.

        Retorna:
            dict: Los datos limpios del formulario.
        """

        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data
