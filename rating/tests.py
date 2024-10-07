from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from content.models import Content, Category
from django.utils import timezone
from rating.models import Rating

class RatingTestCase(TestCase):
    """
    Pruebas para la funcionalidad de calificación de contenido.
    """

    def setUp(self):
        """
        Configura los datos necesarios para las pruebas, incluyendo un usuario, contenido y categoría de prueba.
        """
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

    def test_rate_content_unauthenticated(self):
        """
        Asegura que un usuario no autenticado no pueda calificar un contenido.
        """
        response = self.client.post(self.url, {'rating': 5})
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'Para poder puntuar contenidos debes estar registrado'})

    def test_rate_content_authenticated_valid(self):
        """
        Asegura que un usuario autenticado pueda calificar un contenido con un valor válido (1-5).
        """
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(self.url, {'rating': 4})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': 4})

        # Verificar que la calificación fue registrada en la base de datos
        rating = Rating.objects.get(user=self.user, content=self.content)
        self.assertEqual(rating.rating, 4)

    def test_rate_content_invalid_rating(self):
        """
        Asegura que un usuario pueda calificar un contenido, incluso con un valor fuera de rango (sin validar rango).
        """
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(self.url, {'rating': 10})  # Valor fuera de rango, pero permitido por la vista actual
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'message': 'Calificación guardada correctamente', 'rating': 10})

        # Verificar que la calificación fue registrada en la base de datos con el valor fuera de rango
        rating = Rating.objects.get(user=self.user, content=self.content)
        self.assertEqual(rating.rating, 10)

    def test_update_existing_rating(self):
        """
        Asegura que un usuario pueda actualizar su calificación previa en lugar de crear una nueva.
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

    def test_missing_rating_value(self):
        """
        Asegura que se devuelva un error si no se proporciona un valor de calificación.
        """
        self.client.login(email='testuser@example.com', password='testpassword123')
        response = self.client.post(self.url)  # No se proporciona 'rating'
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'status': 'error', 'message': 'No se proporcionó una calificación'})
