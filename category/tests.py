from django.test import TestCase
from app.models import CustomUser
from app.signals import cache_previous_user, post_save_user_handler
from .models import Category
from django.db import IntegrityError
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from .signals import cache_previous_category, post_save_category_handler, cache_category_before_delete, handle_category_after_delete


class CategoryModelTests(TestCase):
    """
    Clase de pruebas para el modelo Category.

    Esta clase contiene una serie de pruebas unitarias para validar la creación y los atributos del modelo Category,
    incluyendo la verificación de valores predeterminados, restricciones de longitud y valores inválidos.

    Métodos:
        setUp: Configuración inicial para todas las pruebas. Define un diccionario con datos válidos para crear instancias de Category.
        test_create_category: Verifica que una categoría se cree correctamente con datos válidos.
        test_create_category_without_price: Prueba la creación de una categoría sin precio para tipos que no son de pago.
        test_create_public_category: Prueba la creación de una categoría de tipo público.
        test_create_suscription_category: Prueba la creación de una categoría de tipo suscriptor.
        test_default_is_active: Verifica que el valor predeterminado de `is_active` sea True si no se especifica.
        test_default_is_moderated: Verifica que el valor predeterminado de `is_moderated` sea True si no se especifica.
        test_invalid_price_value: Verifica que no se permita establecer un precio negativo, lo que debería lanzar un IntegrityError.
        test_max_length_name: Verifica que no se pueda exceder la longitud máxima del campo `name`, lo que debería lanzar una excepción.
        test_max_length_type: Verifica que no se pueda exceder la longitud máxima del campo `type`, lo que debería lanzar una excepción.
    """

    def setUp(self):
        """
        Configura el estado inicial para todas las pruebas.

        Define un diccionario `category_data` con datos válidos para crear instancias de Category,
        incluyendo nombre, descripción, estado, moderación, precio y tipo de categoría.
        """
        # Configuración inicial para todas las pruebas
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)
        self.category_data = {
            'name': 'Tecnología',
            'description': 'Categoría sobre tecnología y gadgets',
            'is_active': True,
            'is_moderated': True,
            'price': 49,
            'type': Category.TypeChoices.paid
        }

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    def test_create_category(self):
        """
        Prueba la creación de una categoría con datos válidos.

        Verifica que los atributos de la categoría creada coincidan con los valores esperados.
        Comprueba que `name`, `description`, `is_active`, `is_moderated`, `price` y `type` se establezcan correctamente.
        """

        # Prueba de creación de una categoría con datos válidos
        category = Category.objects.create(**self.category_data)
        self.assertEqual(
            category.name, self.category_data['name'],
            msg="El nombre de la categoría no coincide con el valor esperado."
        )
        self.assertEqual(
            category.description, self.category_data['description'],
            msg="La descripción de la categoría no coincide con el valor esperado."
        )
        self.assertTrue(
            category.is_active,
            msg="El valor predeterminado de 'is_active' debería ser True."
        )
        self.assertTrue(
            category.is_moderated,
            msg="El valor predeterminado de 'is_moderated' debería ser True."
        )
        self.assertEqual(
            category.price, self.category_data['price'],
            msg="El precio de la categoría no coincide con el valor esperado."
        )
        self.assertEqual(
            category.type, Category.TypeChoices.paid,
            msg="El tipo de categoría no coincide con 'Categoría de Pago'."
        )

    def test_create_category_without_price(self):
        """
        Prueba la creación de una categoría sin un precio establecido.

        Verifica que el campo `price` sea None cuando no se proporciona un valor para categorías que no requieren precio.
        """

        # Prueba de creación de una categoría sin precio
        self.category_data['price'] = None
        category = Category.objects.create(**self.category_data)
        self.assertIsNone(
            category.price,
            msg="El precio de la categoría debería ser None cuando no se establece."
        )

    def test_create_public_category(self):
        """
        Prueba la creación de una categoría pública.

        Cambia el tipo de la categoría a `public` y verifica que el tipo se establezca correctamente en la instancia creada.
        """

        # Prueba de creación de una categoría pública
        self.category_data['type'] = Category.TypeChoices.public
        category = Category.objects.create(**self.category_data)
        self.assertEqual(
            category.type, Category.TypeChoices.public,
            msg="El tipo de categoría no coincide con 'Categoría Pública'."
        )

    def test_create_suscription_category(self):
        """
        Prueba la creación de una categoría para suscriptores.

        Cambia el tipo de la categoría a `suscription` y verifica que el tipo se establezca correctamente en la instancia creada.
        """
        # Prueba de creación de una categoría para suscriptores
        self.category_data['type'] = Category.TypeChoices.suscription
        category = Category.objects.create(**self.category_data)
        self.assertEqual(
            category.type, Category.TypeChoices.suscription,
            msg="El tipo de categoría no coincide con 'Categoría para Suscriptor'."
        )

    def test_default_is_active(self):
        """
        Verifica el valor predeterminado de `is_active` en la categoría.

        Elimina `is_active` del diccionario de datos y comprueba que el valor predeterminado sea True en la instancia creada.
        """
        # Prueba para verificar el valor predeterminado de is_active
        del self.category_data['is_active']
        category = Category.objects.create(**self.category_data)
        self.assertTrue(
            category.is_active,
            msg="El valor predeterminado de 'is_active' debería ser True."
        )

    def test_default_is_moderated(self):
        """
        Verifica el valor predeterminado de `is_moderated` en la categoría.

        Elimina `is_moderated` del diccionario de datos y comprueba que el valor predeterminado sea True en la instancia creada.
        """
        # Prueba para verificar el valor predeterminado de is_moderated
        del self.category_data['is_moderated']
        category = Category.objects.create(**self.category_data)
        self.assertTrue(
            category.is_moderated,
            msg="El valor predeterminado de 'is_moderated' debería ser True."
        )

    def test_invalid_price_value(self):
        """
        Verifica que no se permita establecer un precio negativo para la categoría.

        Intenta crear una categoría con un precio negativo y verifica que se lance un `IntegrityError`.
        """
        # Prueba para verificar que no se puede establecer un precio negativo
        self.category_data['price'] = -10
        with self.assertRaises(IntegrityError, msg="Debería lanzar IntegrityError al establecer un precio negativo."):
            Category.objects.create(**self.category_data)

    def test_max_length_name(self):
        """
        Prueba la restricción de longitud máxima del campo `name`.

        Intenta crear una categoría con un nombre que excede los 255 caracteres y verifica que se lance una excepción.
        """
        # Prueba para verificar la longitud máxima del campo nombre
        self.category_data['name'] = 'A' * 256
        with self.assertRaises(Exception, msg="Debería lanzar una excepción al exceder la longitud máxima del nombre."):
            Category.objects.create(**self.category_data)

    def test_max_length_type(self):
        """
        Prueba la restricción de longitud máxima del campo `type`.

        Intenta crear una categoría con un valor de `type` que excede los 10 caracteres y verifica que se lance una excepción.
        """
        # Establece un valor que exceda la longitud máxima permitida
        self.category_data['type'] = 'A' * 11  # 11 caracteres excede el max_length de 10
        with self.assertRaises(Exception, msg="Debería lanzar una excepción al exceder la longitud máxima del tipo."):
            Category.objects.create(**self.category_data)
