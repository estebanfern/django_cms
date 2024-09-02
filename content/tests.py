from django.test import TestCase
from django.utils import timezone
from .models import Content
from category.models import Category
from app.models import CustomUser
from django.core.exceptions import ValidationError

class ContentModelTests(TestCase):
    """
    Clase de pruebas para el modelo Content.

    Esta clase contiene una serie de pruebas unitarias para validar la creación y los atributos del modelo Content,
    incluyendo la verificación de valores predeterminados, restricciones de longitud y validaciones personalizadas.

    Métodos:
        setUp: Configuración inicial para todas las pruebas. Crea un autor, una categoría y un conjunto de datos válidos para crear instancias de Content.
        test_create_content: Verifica que un contenido se cree correctamente con datos válidos.
        test_default_is_active: Verifica que el campo `is_active` tenga el valor predeterminado de True al crear un contenido.
        test_default_state: Verifica que el estado predeterminado del contenido sea 'Borrador' si no se especifica otro.
        test_expired_content: Verifica que el contenido se considere expirado si la fecha de expiración es en el pasado.
        test_invalid_state_value: Verifica que se lance un ValidationError si se asigna un estado no válido al contenido.
        test_title_max_length: Verifica que no se pueda exceder la longitud máxima del campo `title`, lo que debería lanzar una excepción.
        test_date_expire_in_future: Verifica que la fecha de expiración esté en el futuro en relación con la fecha de creación.
    """

    def setUp(self):
        """
        Configura el estado inicial para todas las pruebas.

        Crea un autor y una categoría de prueba, y define un diccionario `content_data` con datos válidos
        para crear instancias de Content, incluyendo título, resumen, categoría, autor, estado de activación,
        fecha de expiración y estado de publicación.
        """

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
        """
        Prueba la creación de un contenido con datos válidos.

        Verifica que los atributos del contenido creado coincidan con los valores esperados,
        incluyendo título, resumen, categoría, autor, estado de activación y estado de publicación.
        """

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
        """
        Verifica el valor predeterminado del campo `is_active` en el contenido.

        Elimina `is_active` del diccionario de datos y comprueba que el valor predeterminado
        sea True en la instancia creada.
        """

        # Prueba para verificar el valor predeterminado de is_active
        del self.content_data['is_active']
        content = Content.objects.create(**self.content_data)
        self.assertTrue(
            content.is_active,
            msg="El campo 'is_active' debería ser True por defecto al crear un contenido."
        )

    def test_default_state(self):
        """
        Verifica el estado predeterminado del contenido.

        Elimina `state` del diccionario de datos y comprueba que el estado predeterminado
        sea 'Borrador' en la instancia creada.
        """

        # Prueba para verificar el estado predeterminado (Borrador)
        del self.content_data['state']
        content = Content.objects.create(**self.content_data)
        self.assertEqual(
            content.state, Content.StateChoices.draft,
            msg="El estado predeterminado del contenido debería ser 'Borrador'."
        )

    def test_expired_content(self):
        """
        Prueba para verificar la expiración de un contenido.

        Cambia la fecha de expiración del contenido a una fecha en el pasado y verifica
        que el contenido se considere expirado.
        """

        # Prueba para verificar la expiración de un contenido
        self.content_data['date_expire'] = timezone.now() - timezone.timedelta(days=1)
        content = Content.objects.create(**self.content_data)
        self.assertLess(
            content.date_expire, timezone.now(),
            msg="La fecha de expiración debería ser en el pasado para un contenido expirado."
        )

    def test_invalid_state_value(self):
        """
        Verifica que el campo `state` del contenido tenga un valor válido.

        Asigna un estado no válido al contenido y verifica que se lance un ValidationError
        al llamar a la validación personalizada `clean()`.
        """

        # Prueba para verificar que el campo state tenga un valor válido
        self.content_data['state'] = 'Invalid'
        content = Content(**self.content_data)
        with self.assertRaises(ValidationError, msg="Debería lanzar ValidationError al asignar un estado no válido."):
            content.clean()  # Llama a la validación para verificar el estado

    def test_title_max_length(self):
        """
        Prueba la restricción de longitud máxima del campo `title`.

        Intenta crear un contenido con un título que excede los 255 caracteres y verifica
        que se lance una excepción.
        """

        # Prueba para verificar la longitud máxima del campo título
        self.content_data['title'] = 'A' * 256
        with self.assertRaises(
            Exception,
            msg="Debería lanzar una excepción al exceder la longitud máxima del título."
        ):
            Content.objects.create(**self.content_data)

    def test_date_expire_in_future(self):
        """
        Verifica que la fecha de expiración del contenido esté en el futuro.

        Comprueba que la fecha de expiración sea posterior a la fecha de creación
        para asegurar la validez temporal del contenido.
        """

        # Prueba para verificar que la fecha de expiración esté en el futuro
        content = Content.objects.create(**self.content_data)
        self.assertGreater(
            content.date_expire, content.date_create,
            msg="La fecha de expiración debería ser posterior a la fecha de creación."
        )
