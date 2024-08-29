from time import sleep

from django.test import TestCase, override_settings
from django.core.files.storage import default_storage
# Create your tests here.
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
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

        # Verifica que la imagen se haya subido correctamente

        # Verifica que la imagen esté en la URL correcta (S3)
        print(default_storage.__class__.__name__)
        expected_url = f"{settings.MEDIA_URL}profile_pics/test.jpg"
        # print(f'Expected URL: {expected_url}')
        print(f"Image uploaded to: {self.user.photo.url}")
        # self.assertEqual(self.user.photo.url, expected_url)



