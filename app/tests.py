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
    Pruebas para la subida de fotos de perfil de usuario.

    Hereda de:
        TestCase: Clase base para las pruebas unitarias en Django.

    Métodos:
        setUp: Configura un usuario de prueba antes de cada test.
        test_profile_picture_upload: Verifica que se pueda subir una foto de perfil correctamente.
    """

    def setUp(self):
        """
        Configura un usuario de prueba antes de cada test.

        Acciones:
            - Crea un usuario con un correo electrónico, nombre y contraseña específicos.
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
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    @override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage')
    def test_profile_picture_upload(self):
        """
        Verifica que se pueda subir una foto de perfil correctamente.

        Acciones:
            - Carga una imagen de prueba y la asigna al campo `photo` del usuario.
            - Guarda el usuario con la imagen subida.
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
    Pruebas para el formulario de creación de usuarios personalizados.

    Hereda de:
        TestCase: Clase base para las pruebas unitarias en Django.

    Métodos:
        test_valid_form: Verifica que el formulario sea válido con datos correctos.
        test_invalid_password_confirmation: Verifica que el formulario sea inválido si las contraseñas no coinciden.
    """

    def setUp(self):
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_valid_form(self):
        """
        Verifica que el formulario sea válido con datos correctos.

        Acciones:
            - Rellena el formulario con datos válidos.
            - Guarda el usuario y verifica que los datos guardados sean correctos.
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
        Verifica que el formulario sea inválido si las contraseñas no coinciden.

        Acciones:
            - Rellena el formulario con contraseñas diferentes.
            - Verifica que el formulario no sea válido y que el error se encuentre en el campo `password2`.
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
    Pruebas para el formulario de autenticación personalizado.

    Hereda de:
        TestCase: Clase base para las pruebas unitarias en Django.

    Métodos:
        setUp: Configura un usuario de prueba antes de cada test.
        test_valid_form: Verifica que el formulario sea válido con credenciales correctas.
        test_invalid_password: Verifica que el formulario sea inválido con una contraseña incorrecta.
        test_missing_username: Verifica que el formulario sea inválido si falta el correo electrónico.
        test_missing_password: Verifica que el formulario sea inválido si falta la contraseña.
        test_inactive_user: Verifica que el formulario sea inválido si el usuario está desactivado.
    """

    def setUp(self):
        """
        Configura un usuario de prueba antes de cada test.

        Acciones:
            - Crea un usuario con un correo electrónico, nombre y contraseña específicos.
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
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_valid_form(self):
        """
        Verifica que el formulario sea válido con credenciales correctas.

        Acciones:
            - Rellena el formulario con un correo electrónico y contraseña válidos.
            - Verifica que el formulario sea válido.
        """

        form_data = {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con credenciales correctas")

    def test_invalid_password(self):
        """
        Verifica que el formulario sea inválido con una contraseña incorrecta.

        Acciones:
            - Rellena el formulario con una contraseña incorrecta.
            - Verifica que el formulario no sea válido y que haya un error general de autenticación.
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
        Verifica que el formulario sea inválido si falta el correo electrónico.

        Acciones:
            - Rellena el formulario sin un correo electrónico.
            - Verifica que el formulario no sea válido y que el error se encuentre en el campo `username`.
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
        Verifica que el formulario sea inválido si falta la contraseña.

        Acciones:
            - Rellena el formulario sin una contraseña.
            - Verifica que el formulario no sea válido y que el error se encuentre en el campo `password`.
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
        Verifica que el formulario sea inválido si el usuario está desactivado.

        Acciones:
            - Desactiva el usuario de prueba.
            - Rellena el formulario con credenciales válidas.
            - Verifica que el formulario no sea válido.
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
    Pruebas para el formulario de actualización de perfil.

    Hereda de:
        TestCase: Clase base para las pruebas unitarias en Django.

    Métodos:
        setUp: Configura un usuario de prueba antes de cada test.
        test_update_name_and_about: Verifica que se puedan actualizar los campos `name` y `about`.
    """

    def setUp(self):
        """
        Configura un usuario de prueba antes de cada test.

        Acciones:
            - Crea un usuario con un correo electrónico, nombre, contraseña y descripción específicos.
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
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_update_name_and_about(self):
        """
        Verifica que se puedan actualizar los campos `name` y `about`.

        Acciones:
            - Rellena el formulario con un nuevo nombre y descripción.
            - Guarda el formulario y verifica que los datos del usuario se actualicen correctamente.
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
    Pruebas para el formulario de cambio de contraseña.

    Hereda de:
        TestCase: Clase base para las pruebas unitarias en Django.

    Métodos:
        setUp: Configura un usuario de prueba antes de cada test.
        test_valid_password_change: Verifica que el formulario sea válido con las contraseñas correctas.
        test_incorrect_current_password: Verifica que el formulario sea inválido si la contraseña actual es incorrecta.
        test_new_passwords_do_not_match: Verifica que el formulario sea inválido si las nuevas contraseñas no coinciden.
        test_new_password_same_as_current: Verifica que el formulario sea inválido si la nueva contraseña es igual a la actual.
        test_missing_current_password: Verifica que el formulario sea inválido si falta la contraseña actual.
        test_missing_new_password: Verifica que el formulario sea inválido si faltan las nuevas contraseñas.
        test_short_new_password: Verifica que el formulario sea inválido si la nueva contraseña es demasiado corta.
    """

    def setUp(self):
        """
        Configura un usuario de prueba antes de cada test.

        Acciones:
            - Crea un usuario con un correo electrónico, nombre y contraseña específicos.
        """
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='oldpassword123'
        )

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        super().tearDown()

    def test_valid_password_change(self):
        """
        Verifica que el formulario sea válido con las contraseñas correctas.

        Acciones:
            - Rellena el formulario con la contraseña actual y nuevas contraseñas válidas.
            - Guarda el formulario y verifica que la contraseña del usuario haya cambiado.
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
        Verifica que el formulario sea inválido si la contraseña actual es incorrecta.

        Acciones:
            - Rellena el formulario con una contraseña actual incorrecta.
            - Verifica que el formulario no sea válido.
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
        Verifica que el formulario sea inválido si las nuevas contraseñas no coinciden.

        Acciones:
            - Rellena el formulario con contraseñas nuevas diferentes.
            - Verifica que el formulario no sea válido.
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
        Verifica que el formulario sea inválido si la nueva contraseña es igual a la actual.

        Acciones:
            - Rellena el formulario con una nueva contraseña igual a la actual.
            - Verifica que el formulario no sea válido.
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
        Verifica que el formulario sea inválido si falta la contraseña actual.

        Acciones:
            - Rellena el formulario sin la contraseña actual.
            - Verifica que el formulario no sea válido.
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
        Verifica que el formulario sea inválido si faltan las nuevas contraseñas.

        Acciones:
            - Rellena el formulario sin las nuevas contraseñas.
            - Verifica que el formulario no sea válido.
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
        Verifica que el formulario sea inválido si la nueva contraseña es demasiado corta.

        Acciones:
            - Rellena el formulario con una nueva contraseña que tiene menos de 8 caracteres.
            - Verifica que el formulario no sea válido.
        """

        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'corto',
            'confirm_new_password': 'corto'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si la contraseña nueva tiene menos de 8 carácteres.")
