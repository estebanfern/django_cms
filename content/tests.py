from django.test import TestCase
from django.utils import timezone
from .models import Content
from category.models import Category
from app.models import CustomUser
from django.core.exceptions import ValidationError


class ContentModelTests(TestCase):

    def setUp(self):
        # Crear un autor y una categoría de prueba
        self.author = CustomUser.objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='password123'
        )
        self.category = Category.objects.create(
            name='Tecnología',
            description='Categoría sobre tecnología',
            is_active=True,
            is_moderated=True,
            type=Category.TypeChoices.paid
        )
        self.content_data = {
            'title': 'Introducción a la IA',
            'summary': 'Un resumen sobre los fundamentos de la inteligencia artificial',
            'category': self.category,
            'autor': self.author,
            'is_active': True,
            'date_expire': timezone.now() + timezone.timedelta(days=365),
            'state': Content.StateChoices.publish
        }

    def test_create_content(self):
        # Prueba de creación de un contenido con datos válidos
        content = Content.objects.create(**self.content_data)
        self.assertEqual(content.title, self.content_data['title'])
        self.assertEqual(content.summary, self.content_data['summary'])
        self.assertEqual(content.category, self.content_data['category'])
        self.assertEqual(content.autor, self.content_data['autor'])
        self.assertTrue(content.is_active)
        self.assertEqual(content.state, Content.StateChoices.publish)

    def test_default_is_active(self):
        # Prueba para verificar el valor predeterminado de is_active
        del self.content_data['is_active']
        content = Content.objects.create(**self.content_data)
        self.assertTrue(content.is_active)

    def test_default_state(self):
        # Prueba para verificar el estado predeterminado (Borrador)
        del self.content_data['state']
        content = Content.objects.create(**self.content_data)
        self.assertEqual(content.state, Content.StateChoices.draft)

    def test_expired_content(self):
        # Prueba para verificar la expiración de un contenido
        self.content_data['date_expire'] = timezone.now() - timezone.timedelta(days=1)
        content = Content.objects.create(**self.content_data)
        self.assertLess(content.date_expire, timezone.now())

    def test_invalid_state_value(self):
        # Prueba para verificar que el campo state tenga un valor válido
        self.content_data['state'] = 'Invalid'
        content = Content(**self.content_data)
        with self.assertRaises(ValidationError, msg="Debería lanzar ValidationError al asignar un estado no válido."):
            content.clean()  # Llama a la validación para verificar el estado
            content.save()  # Este paso ya llamaría a clean() debido al ajuste en el modelo

    def test_title_max_length(self):
        # Prueba para verificar la longitud máxima del campo título
        self.content_data['title'] = 'A' * 256
        with self.assertRaises(Exception):
            Content.objects.create(**self.content_data)

    def test_date_expire_in_future(self):
        # Prueba para verificar que la fecha de expiración esté en el futuro
        content = Content.objects.create(**self.content_data)
        self.assertGreater(content.date_expire, content.date_create)
