from django.test import TestCase
from .models import Category
from django.db import IntegrityError

class CategoryModelTests(TestCase):

    def setUp(self):
        # Configuración inicial para todas las pruebas
        self.category_data = {
            'name': 'Tecnología',
            'description': 'Categoría sobre tecnología y gadgets',
            'is_active': True,
            'is_moderated': True,
            'price': 49,
            'type': Category.TypeChoices.paid
        }

    def test_create_category(self):
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
        # Prueba de creación de una categoría sin precio
        self.category_data['price'] = None
        category = Category.objects.create(**self.category_data)
        self.assertIsNone(
            category.price,
            msg="El precio de la categoría debería ser None cuando no se establece."
        )

    def test_create_public_category(self):
        # Prueba de creación de una categoría pública
        self.category_data['type'] = Category.TypeChoices.public
        category = Category.objects.create(**self.category_data)
        self.assertEqual(
            category.type, Category.TypeChoices.public,
            msg="El tipo de categoría no coincide con 'Categoría Pública'."
        )

    def test_create_suscription_category(self):
        # Prueba de creación de una categoría para suscriptores
        self.category_data['type'] = Category.TypeChoices.suscription
        category = Category.objects.create(**self.category_data)
        self.assertEqual(
            category.type, Category.TypeChoices.suscription,
            msg="El tipo de categoría no coincide con 'Categoría para Suscriptor'."
        )

    def test_default_is_active(self):
        # Prueba para verificar el valor predeterminado de is_active
        del self.category_data['is_active']
        category = Category.objects.create(**self.category_data)
        self.assertTrue(
            category.is_active,
            msg="El valor predeterminado de 'is_active' debería ser True."
        )

    def test_default_is_moderated(self):
        # Prueba para verificar el valor predeterminado de is_moderated
        del self.category_data['is_moderated']
        category = Category.objects.create(**self.category_data)
        self.assertTrue(
            category.is_moderated,
            msg="El valor predeterminado de 'is_moderated' debería ser True."
        )

    def test_invalid_price_value(self):
        # Prueba para verificar que no se puede establecer un precio negativo
        self.category_data['price'] = -10
        with self.assertRaises(IntegrityError, msg="Debería lanzar IntegrityError al establecer un precio negativo."):
            Category.objects.create(**self.category_data)

    def test_max_length_name(self):
        # Prueba para verificar la longitud máxima del campo nombre
        self.category_data['name'] = 'A' * 256
        with self.assertRaises(Exception, msg="Debería lanzar una excepción al exceder la longitud máxima del nombre."):
            Category.objects.create(**self.category_data)

    def test_max_length_type(self):
        # Establece un valor que exceda la longitud máxima permitida
        self.category_data['type'] = 'A' * 11  # 11 caracteres excede el max_length de 10
        with self.assertRaises(Exception, msg="Debería lanzar una excepción al exceder la longitud máxima del tipo."):
            Category.objects.create(**self.category_data)
