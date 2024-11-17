from django.db.models.signals import pre_save, post_save
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from app.forms import ChangePasswordForm, CustomUserCreationForm, ProfileUpdateForm
from django.contrib.auth import get_user_model
from app.forms import CustomAuthenticationForm
import os

from app.models import CustomUser
from app.signals import cache_previous_user, post_save_user_handler


@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage')
class ProfilePictureUploadTest(TestCase):
    """
    Clase de pruebas para la funcionalidad de carga de imágenes de perfil de usuario.

    :raises: Puede lanzar excepciones relacionadas con la creación de datos de prueba.
    """

    def setUp(self):
        """
        Configura el entorno de pruebas para la carga de imágenes de perfil.

        :raises: Puede lanzar excepciones relacionadas con la creación de datos de prueba.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        # Crea un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )

    def tearDown(self):
        """
        Limpia el entorno de pruebas reconectando las señales.
        """

        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    @override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage')
    def test_profile_picture_upload(self):
        """
        Prueba la carga de una imagen de perfil para un usuario.

        :return: Verifica que la imagen se asocie correctamente al campo `photo` del usuario.
        :rtype: None
        """

        # Ruta de la imagen de prueba
        image_path = os.path.join(settings.BASE_DIR, 'static', 'test.jpg')

        # Carga la imagen en un SimpleUploadedFile
        with open(image_path, 'rb') as image_file:
            uploaded_image = SimpleUploadedFile(
                name='test.jpg',
                content=image_file.read(),
                content_type='image/jpeg'
            )

        # Asigna la imagen al campo `photo` del usuario
        self.user.photo.save('test.jpg', uploaded_image)
        self.user.save()

class CustomUserCreationFormTest(TestCase):
    """
    Clase de pruebas para el formulario de creación de usuarios personalizados.
    """

    def setUp(self):
        """
        Configura el entorno de pruebas desconectando las señales para evitar efectos secundarios.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)

    def tearDown(self):
        """
        Reconecta las señales después de completar las pruebas.
        """

        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_valid_form(self):
        """
        Prueba que el formulario de creación de usuario sea válido con datos correctos.

        :return: Verifica que se cree un usuario con los datos proporcionados.
        :rtype: None
        """

        form_data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password1': 'strong_password_123',
            'password2': 'strong_password_123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.name, 'Test User')

    def test_invalid_password_confirmation(self):
        """
        Prueba que el formulario sea inválido si las contraseñas no coinciden.

        :return: Verifica que se genere un error en el campo `password2`.
        :rtype: None
        """

        form_data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password1': 'strong_password_123',
            'password2': 'different_password'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class CustomAuthenticationFormTest(TestCase):
    """
    Clase de pruebas para el formulario de autenticación de usuarios personalizados.
    """

    def setUp(self):
        """
        Configura el entorno de pruebas creando un usuario de prueba.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )

    def tearDown(self):
        """
        Reconecta las señales después de completar las pruebas.
        """

        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_valid_form(self):
        """
        Prueba que el formulario de autenticación sea válido con credenciales correctas.

        :return: Verifica que el formulario sea válido.
        :rtype: None
        """

        form_data = {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con credenciales correctas")

    def test_invalid_password(self):
        """
        Prueba que el formulario sea inválido con una contraseña incorrecta.

        :return: Verifica que se genere un error relacionado con la autenticación incorrecta.
        :rtype: None
        """

        form_data = {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido con una contraseña incorrecta")
        self.assertIn('__all__', form.errors, "Debería haber un error relacionado con la autenticación incorrecta")

    def test_missing_username(self):
        """
        Prueba que el formulario sea inválido si falta el correo electrónico.

        :return: Verifica que se genere un error en el campo `username`.
        :rtype: None
        """

        form_data = {
            'username': '',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si falta el correo electrónico")
        self.assertIn('username', form.errors, "Debería haber un error relacionado con la falta del correo electrónico")

    def test_missing_password(self):
        """
        Prueba que el formulario sea inválido si falta la contraseña.

        :return: Verifica que se genere un error en el campo `password`.
        :rtype: None
        """

        form_data = {
            'username': 'testuser@example.com',
            'password': ''
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si falta la contraseña")
        self.assertIn('password', form.errors, "Debería haber un error relacionado con la falta de contraseña")

    def test_inactive_user(self):
        """
        Prueba que el formulario sea inválido si el usuario está desactivado.

        :return: Verifica que el formulario no sea válido.
        :rtype: None
        """

        self.user.is_active = False
        self.user.save()

        form_data = {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si el usuario está desactivado")


class ProfileUpdateFormTest(TestCase):
    """
    Clase de pruebas para el formulario de actualización de perfil de usuario.
    """

    def setUp(self):
        """
        Configura el entorno de pruebas creando un usuario de prueba con datos iniciales.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123',
            about='Old about me',
        )

    def tearDown(self):
        """
        Reconecta las señales después de completar las pruebas.
        """

        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_update_name_and_about(self):
        """
        Prueba que el formulario permita actualizar el nombre y el campo `about` del perfil.

        :return: Verifica que los datos del usuario se actualicen correctamente.
        :rtype: None
        """

        form_data = {
            'name': 'Updated Name',
            'about': 'Updated about me'
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con nombre y about actualizados")
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated Name')
        self.assertEqual(self.user.about, 'Updated about me')

class ChangePasswordFormTest(TestCase):
    """
    Clase de pruebas para el formulario de cambio de contraseña.
    """

    def setUp(self):
        """
        Configura el entorno de pruebas creando un usuario con una contraseña inicial.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='oldpassword123'
        )

    def tearDown(self):
        """
        Reconecta las señales después de completar las pruebas.
        """

        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_valid_password_change(self):
        """
        Prueba que el formulario sea válido con una contraseña actual correcta y nuevas contraseñas válidas.

        :return: Verifica que la contraseña del usuario se actualice correctamente.
        :rtype: None
        """

        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con las contraseñas correctas")
        form.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'), "La contraseña debería haber sido cambiada")

    def test_incorrect_current_password(self):
        """
        Prueba que el formulario sea inválido si la contraseña actual es incorrecta.

        :return: Verifica que el formulario genere un error.
        :rtype: None
        """

        form_data = {
            'current_password': 'wrongpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido con la contraseña actual incorrecta")

    def test_new_passwords_do_not_match(self):
        """
        Prueba que el formulario sea inválido si las nuevas contraseñas no coinciden.

        :return: Verifica que el formulario genere un error.
        :rtype: None
        """

        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'differentpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si las nuevas contraseñas no coinciden")

    def test_new_password_same_as_current(self):
        """
        Prueba que el formulario sea inválido si la nueva contraseña es igual a la actual.

        :return: Verifica que el formulario genere un error.
        :rtype: None
        """

        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'oldpassword123',
            'confirm_new_password': 'oldpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si la nueva contraseña es igual a la actual")

    def test_missing_current_password(self):
        """
        Prueba que el formulario sea inválido si falta la contraseña actual.

        :return: Verifica que el formulario genere un error.
        :rtype: None
        """

        form_data = {
            'current_password': '',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si falta la contraseña actual")

    def test_missing_new_password(self):
        """
        Prueba que el formulario sea inválido si faltan las nuevas contraseñas.

        :return: Verifica que el formulario genere un error.
        :rtype: None
        """

        form_data = {
            'current_password': 'oldpassword123',
            'new_password': '',
            'confirm_new_password': ''
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si faltan las nuevas contraseñas")

    def test_short_new_password(self):
        """
        Prueba que el formulario sea inválido si la nueva contraseña tiene menos de 8 caracteres.

        :return: Verifica que el formulario genere un error.
        :rtype: None
        """

        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'corto',
            'confirm_new_password': 'corto'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si la contraseña nueva tiene menos de 8 carácteres.")
