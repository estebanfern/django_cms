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
        self.assertEqual(
            content.title, self.content_data['title'],
            msg="El título del contenido no coincide con el valor esperado."
        )
        self.assertEqual(
            content.summary, self.content_data['summary'],
            msg="El resumen del contenido no coincide con el valor esperado."
        )
        self.assertEqual(
            content.category, self.content_data['category'],
            msg="La categoría del contenido no coincide con la esperada."
        )
        self.assertEqual(
            content.autor, self.content_data['autor'],
            msg="El autor del contenido no coincide con el valor esperado."
        )
        self.assertTrue(
            content.is_active,
            msg="El campo 'is_active' debería ser True por defecto."
        )
        self.assertEqual(
            content.state, Content.StateChoices.publish,
            msg="El estado del contenido no coincide con el valor 'Publicado'."
        )

    def test_default_is_active(self):
        # Prueba para verificar el valor predeterminado de is_active
        del self.content_data['is_active']
        content = Content.objects.create(**self.content_data)
        self.assertTrue(
            content.is_active,
            msg="El campo 'is_active' debería ser True por defecto al crear un contenido."
        )

    def test_default_state(self):
        # Prueba para verificar el estado predeterminado (Borrador)
        del self.content_data['state']
        content = Content.objects.create(**self.content_data)
        self.assertEqual(
            content.state, Content.StateChoices.draft,
            msg="El estado predeterminado del contenido debería ser 'Borrador'."
        )

    def test_expired_content(self):
        # Prueba para verificar la expiración de un contenido
        self.content_data['date_expire'] = timezone.now() - timezone.timedelta(days=1)
        content = Content.objects.create(**self.content_data)
        self.assertLess(
            content.date_expire, timezone.now(),
            msg="La fecha de expiración debería ser en el pasado para un contenido expirado."
        )

    def test_invalid_state_value(self):
        # Prueba para verificar que el campo state tenga un valor válido
        self.content_data['state'] = 'Invalid'
        content = Content(**self.content_data)
        with self.assertRaises(ValidationError, msg="Debería lanzar ValidationError al asignar un estado no válido."):
            content.clean()  # Llama a la validación para verificar el estado

    def test_title_max_length(self):
        # Prueba para verificar la longitud máxima del campo título
        self.content_data['title'] = 'A' * 256
        with self.assertRaises(
            Exception,
            msg="Debería lanzar una excepción al exceder la longitud máxima del título."
        ):
            Content.objects.create(**self.content_data)

    def test_date_expire_in_future(self):
        # Prueba para verificar que la fecha de expiración esté en el futuro
        content = Content.objects.create(**self.content_data)
        self.assertGreater(
            content.date_expire, content.date_create,
            msg="La fecha de expiración debería ser posterior a la fecha de creación."
        )
