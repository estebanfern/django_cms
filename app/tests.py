from django.test import TestCase, override_settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from app.forms import ChangePasswordForm, CustomUserCreationForm, ProfileUpdateForm
from django.contrib.auth import get_user_model
from app.forms import CustomAuthenticationForm
import os

@override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage')
class ProfilePictureUploadTest(TestCase):

    def setUp(self):
        # Crea un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )

    @override_settings(DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage')
    def test_profile_picture_upload(self):
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

    def test_valid_form(self):
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

    def setUp(self):
        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )

    def test_valid_form(self):
        form_data = {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con credenciales correctas")

    def test_invalid_password(self):
        form_data = {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido con una contraseña incorrecta")
        self.assertIn('__all__', form.errors, "Debería haber un error relacionado con la autenticación incorrecta")

    def test_missing_username(self):
        form_data = {
            'username': '',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si falta el correo electrónico")
        self.assertIn('username', form.errors, "Debería haber un error relacionado con la falta del correo electrónico")

    def test_missing_password(self):
        form_data = {
            'username': 'testuser@example.com',
            'password': ''
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si falta la contraseña")
        self.assertIn('password', form.errors, "Debería haber un error relacionado con la falta de contraseña")

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        form_data = {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid(), "El formulario no debería ser válido si el usuario está desactivado")


class ProfileUpdateFormTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123',
            about='Old about me',
        )

    def test_update_name_and_about(self):
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

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='oldpassword123'
        )

    def test_valid_password_change(self):
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
        form_data = {
            'current_password': 'wrongpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido con la contraseña actual incorrecta")

    def test_new_passwords_do_not_match(self):
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'differentpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si las nuevas contraseñas no coinciden")

    def test_new_password_same_as_current(self):
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': 'oldpassword123',
            'confirm_new_password': 'oldpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si la nueva contraseña es igual a la actual")

    def test_missing_current_password(self):
        form_data = {
            'current_password': '',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123'
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si falta la contraseña actual")

    def test_missing_new_password(self):
        form_data = {
            'current_password': 'oldpassword123',
            'new_password': '',
            'confirm_new_password': ''
        }
        form = ChangePasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid(), "El formulario debería ser inválido si faltan las nuevas contraseñas")
