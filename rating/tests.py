from unittest.mock import patch
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from app.models import CustomUser
from app.signals import cache_previous_user, post_save_user_handler
from category.signals import cache_previous_category, post_save_category_handler, cache_category_before_delete, handle_category_after_delete
from content.models import Content, Category
from django.utils import timezone
from rating.models import Rating

class RatingTestCase(TestCase):
    """
    Pruebas para la funcionalidad de calificación de contenido.

    :Attributes:
        - **user** (:class:`CustomUser`): Usuario de prueba que realiza las calificaciones.
        - **category** (:class:`Category`): Categoría de prueba para asociar al contenido.
        - **content** (:class:`Content`): Contenido de prueba al que se le aplicarán las calificaciones.
        - **url** (str): URL para realizar las solicitudes de calificación de contenido.

    :Methods:
        - :meth:`setUp`: Configura los datos necesarios para los tests, incluyendo la creación de un usuario, categoría y contenido de prueba.
        - :meth:`tearDown`: Reconecta las señales desconectadas y realiza la limpieza posterior a los tests.
        - :meth:`test_rate_content_unauthenticated`: Verifica que un usuario no autenticado no pueda calificar un contenido.
        - :meth:`test_rate_content_authenticated_valid`: Verifica que un usuario autenticado pueda calificar un contenido con un valor válido (1-5).
        - :meth:`test_update_existing_rating`: Verifica que un usuario pueda actualizar su calificación previa en lugar de crear una nueva.
        - :meth:`test_rate_content_invalid_rating`: Verifica que se pueda registrar una calificación fuera del rango esperado (sin validación de rango).
        - :meth:`test_missing_rating_value`: Verifica que se devuelva un error si no se proporciona un valor de calificación.
    """

    def setUp(self):
        """
        Configura los datos necesarios para las pruebas, incluyendo un usuario, contenido y categoría de prueba.

        Lógica:
            - Desconecta señales para evitar efectos secundarios.
            - Crea un usuario de prueba.
            - Crea una categoría y un contenido de prueba asociados al usuario.
            - Define la URL para las solicitudes de calificación.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)

        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )

        # Crear una categoría y contenido de prueba
        self.category = Category.objects.create(name='Test Category')
        self.content = Content.objects.create(
            title='Test Content',
            summary='Summary of the test content',
            category=self.category,
            autor=self.user,
            date_expire=timezone.now() + timezone.timedelta(days=1),
            content='This is a test content',
        )

        # URL para calificar el contenido
        self.url = reverse('rate_content', args=[self.content.id])

    def tearDown(self):
        """
        Reconecta las señales desconectadas y realiza la limpieza después de cada prueba.

        Lógica:
            - Reconecta las señales desconectadas durante `setUp`.
            - Llama a `tearDown` de la clase base para realizar la limpieza adicional.
        """
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    @patch('rating.views.update_rating_avg.delay')  # Mock the Celery task
    def test_rate_content_unauthenticated(self, mock_update_rating_avg):
        """
        Verifica que un usuario no autenticado no pueda calificar un contenido.

        Lógica:
            - Realiza una solicitud POST sin autenticación a la URL de calificación.
            - Verifica que el estado de la respuesta sea 403 (prohibido).
            - Confirma que el mensaje de error sea el esperado.
            - Verifica que la tarea Celery no haya sido llamada.
        """
        response = self.client.post(self.url, {'rating': 5})
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'Para poder puntuar contenidos debes estar registrado'})
        mock_update_rating_avg.assert_not_called()

    @patch('rating.views.update_rating_avg.delay')  # Mock the Celery task
    def test_rate_content_authenticated_valid(self, mock_update_rating_avg):
        """
        Verifica que un usuario autenticado pueda calificar un contenido con un valor válido (1-5).

        Lógica:
            - Inicia sesión con el usuario de prueba.
            - Realiza una solicitud POST con una calificación válida.
            - Verifica que el estado de la respuesta sea 200 (éxito).
            - Confirma que la calificación fue guardada correctamente en la base de datos.
            - Verifica que la tarea Celery fue llamada una vez.
        """
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(self.url, {'rating': 4})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': 4})

        # Verificar que la calificación fue registrada en la base de datos
        rating = Rating.objects.get(user=self.user, content=self.content)
        self.assertEqual(rating.rating, 4)

        # Ensure that the mocked task was called
        mock_update_rating_avg.assert_called_once_with(self.content.id)

    @patch('rating.views.update_rating_avg.delay')  # Mock the Celery task
    def test_update_existing_rating(self, mock_update_rating_avg):
        """
        Verifica que un usuario pueda actualizar su calificación previa en lugar de crear una nueva.

        Lógica:
            - Inicia sesión y califica el contenido con un valor inicial.
            - Actualiza la calificación con un nuevo valor.
            - Verifica que la calificación haya sido actualizada correctamente.
            - Confirma que la tarea Celery fue llamada dos veces (una para cada calificación).
        """
        # Primero, calificar el contenido con un valor de 3
        self.client.login(email='testuser@example.com', password='testpassword123')
        self.client.post(self.url, {'rating': 3})

        # Ahora, actualizar la calificación a 5
        response = self.client.post(self.url, {'rating': 5})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': 5})

        # Verificar que la calificación fue actualizada
        rating = Rating.objects.get(user=self.user, content=self.content)
        self.assertEqual(rating.rating, 5)

        # Ensure that the mocked task was called twice
        self.assertEqual(mock_update_rating_avg.call_count, 2)

    @patch('rating.views.update_rating_avg.delay')  # Mock the Celery task
    def test_rate_content_invalid_rating(self, mock_update_rating_avg):
        """
        Verifica que se pueda registrar una calificación fuera del rango esperado (sin validación de rango).

        Lógica:
            - Inicia sesión con el usuario de prueba.
            - Realiza una solicitud POST con una calificación fuera de rango (por ejemplo, 10).
            - Verifica que la respuesta sea exitosa y que el valor fuera de rango sea registrado.
            - Confirma que la tarea Celery fue llamada una vez.
        """
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(self.url, {'rating': 10})  # Valor fuera de rango, pero permitido por la vista actual
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': 10})

        # Verificar que la calificación fue registrada en la base de datos con el valor fuera de rango
        rating = Rating.objects.get(user=self.user, content=self.content)
        self.assertEqual(rating.rating, 10)

        # Ensure that the mocked task was called
        mock_update_rating_avg.assert_called_once_with(self.content.id)

    @patch('rating.views.update_rating_avg.delay')  # Mock the Celery task
    def test_missing_rating_value(self, mock_update_rating_avg):
        """
        Verifica que se devuelva un error si no se proporciona un valor de calificación.

        Lógica:
            - Inicia sesión con el usuario de prueba.
            - Realiza una solicitud POST sin proporcionar un valor de calificación.
            - Verifica que el estado de la respuesta sea 400 (error de solicitud).
            - Confirma que el mensaje de error sea el esperado.
            - Verifica que la tarea Celery no haya sido llamada.
        """
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(self.url)  # No se proporciona 'rating'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'No se proporcionó una calificación'})
        mock_update_rating_avg.assert_not_called()
