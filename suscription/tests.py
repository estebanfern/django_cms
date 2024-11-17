from django.test import TestCase
from django.utils.timezone import now
from django.urls import reverse
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from app.models import CustomUser
from category.models import Category
from suscription.models import Suscription
from app.signals import cache_previous_user, post_save_user_handler
from category.signals import cache_previous_category, post_save_category_handler, cache_category_before_delete, handle_category_after_delete
from unittest.mock import patch, MagicMock

class SuscriptionTests(TestCase):
    """
    Clase que contiene pruebas unitarias para verificar el comportamiento del modelo Suscription y las vistas relacionadas.

    Las pruebas incluyen casos para la creación de suscripciones, validación de duplicados, cambios de estado, suscripciones a categorías públicas y de pago, y manejo de webhooks de Stripe.

    :cvar user: Usuario de prueba creado para las pruebas.
    :type user: CustomUser
    :cvar category: Categoría de prueba utilizada para las pruebas de suscripción.
    :type category: Category
    :cvar suscription: Suscripción de prueba inicial configurada durante el setup.
    :type suscription: Suscription
    :cvar mock_signature: Firma simulada utilizada para pruebas de webhooks.
    :type mock_signature: str
    """

    def setUp(self):
        """
        Configura el entorno de prueba aislado.

        Este metodo se ejecuta antes de cada prueba para desconectar señales, crear un usuario de prueba,
        una categoría de prueba y una suscripción inicial.

        :raises Exception: Si ocurre un error durante la configuración inicial.
        """

        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)

        # Crear usuario y categoría de prueba
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="password123"
        )
        self.user.stripe_customer_id = "cus_test_id"  # Asignamos un ID de cliente de Stripe simulado
        self.user.save()

        self.category = Category.objects.create(
            name="Test Category",
            description="Description for testing",
            type=Category.TypeChoices.public,
            is_active=True,
            is_moderated=True
        )

        # Crear suscripción de prueba
        self.suscription = Suscription.objects.create(
            user=self.user,
            category=self.category,
            state=Suscription.SuscriptionState.active,
            date_subscribed=now()
        )

        # Valor simulado para la firma de Stripe
        self.mock_signature = 'test_mocked_signature'

    def tearDown(self):
        """
        Limpia el entorno de prueba.

        Reconecta las señales previamente desconectadas para restaurar el comportamiento normal
        después de la ejecución de cada prueba.
        """
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    def test_create_subscription(self):
        """
        Prueba la creación de una nueva suscripción.

        Verifica que se pueda crear una suscripción para un usuario y categoría dados, y que los valores iniciales
        sean correctos.

        :raises AssertionError: Si los valores creados no coinciden con los esperados.
        """
        Suscription.objects.filter(user=self.user, category=self.category).delete()

        subscription = Suscription.objects.create(
            user=self.user,
            category=self.category,
            state=Suscription.SuscriptionState.active
        )

        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.category, self.category)
        self.assertEqual(subscription.state, Suscription.SuscriptionState.active)

    def test_duplicate_subscription(self):
        """
        Prueba la validación de duplicados en suscripciones.

        Intenta crear una suscripción duplicada para el mismo usuario y categoría, y verifica
        que se genere una excepción debido a la restricción de unicidad.

        :raises Exception: Si se permite crear una suscripción duplicada.
        """
        with self.assertRaises(Exception):
            Suscription.objects.create(
                user=self.user,
                category=self.category,
                state=Suscription.SuscriptionState.active
            )

    def test_change_subscription_state_to_cancelled(self):
        """
        Prueba el cambio de estado de una suscripción a cancelado.

        Cambia el estado de una suscripción existente a "cancelado" y verifica que se actualice correctamente
        en la base de datos.

        :raises AssertionError: Si el estado no se actualiza como se esperaba.
        """
        self.suscription.state = Suscription.SuscriptionState.cancelled
        self.suscription.save()
        self.suscription.refresh_from_db()
        self.assertEqual(self.suscription.state, Suscription.SuscriptionState.cancelled)

    def test_subscribe_to_public_category(self):
        """
        Prueba la suscripción a una categoría pública.

        Simula que un usuario inicia sesión y se suscribe a una categoría pública. Verifica que:
        - La suscripción se crea correctamente.
        - Intentar suscribirse nuevamente genera un error.

        :raises AssertionError: Si los resultados no coinciden con los esperados.
        """
        self.client.login(email=self.user.email, password="password123")

        Suscription.objects.filter(user=self.user, category=self.category).delete()

        response = self.client.post(reverse('suscribe_category', args=[self.category.id]))

        self.assertEqual(response.status_code, 200)
        subscription = Suscription.objects.get(user=self.user, category=self.category)
        self.assertEqual(subscription.state, Suscription.SuscriptionState.active)

        response_duplicate = self.client.post(reverse('suscribe_category', args=[self.category.id]))
        self.assertEqual(response_duplicate.status_code, 400)
        self.assertIn("Ya estás suscrito a esta categoría", response_duplicate.json().get("message"))

    def test_unsubscribe_from_public_category(self):
        """
        Prueba la desuscripción de una categoría pública.

        Simula que un usuario inicia sesión y se desuscribe de una categoría pública. Verifica que:
        - La suscripción sea eliminada correctamente.

        :raises AssertionError: Si la suscripción no se elimina como se esperaba.
        """
        self.client.login(email=self.user.email, password="password123")

        response = self.client.post(reverse('unsuscribe_category', args=[self.category.id]))
        self.assertEqual(response.status_code, 200)

        self.assertFalse(Suscription.objects.filter(user=self.user, category=self.category).exists())

    @patch("suscription.views.create_checkout_session")
    def test_subscribe_to_paid_category_creates_checkout_session(self, mock_create_checkout_session):
        """
        Prueba la creación de sesiones de pago para categorías de pago.

        Configura una categoría como de pago, simula el proceso de suscripción con un usuario autenticado
        y verifica que:
        - Se llame correctamente a la función `create_checkout_session`.
        - La respuesta contenga una URL válida para el checkout.

        :param mock_create_checkout_session: Objeto mock que simula el comportamiento de la función `create_checkout_session`.
        :type mock_create_checkout_session: MagicMock
        :raises AssertionError: Si las llamadas o respuestas no cumplen con lo esperado.
        """
        # Set up a paid category with Stripe price ID
        self.category.type = Category.TypeChoices.paid
        self.category.stripe_price_id = "price_test_id"
        self.category.save()

        # Ensure no active subscription exists before subscribing
        Suscription.objects.filter(user=self.user, category=self.category).delete()

        # Mock session to simulate Stripe checkout
        mock_session = MagicMock()
        mock_session.url = "https://stripe.com/checkout/test"
        mock_create_checkout_session.return_value = mock_session

        # Login and attempt subscription
        self.client.login(email=self.user.email, password="password123")
        response = self.client.post(reverse('suscribe_category', args=[self.category.id]))

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("checkout_url", response.json())
        self.assertEqual(response.json().get("checkout_url"), "https://stripe.com/checkout/test")

        # Ensure create_checkout_session is called with correct arguments
        mock_create_checkout_session.assert_called_once_with(response.wsgi_request, self.category.id)
