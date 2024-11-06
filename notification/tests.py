from django.test import TestCase

# Create your tests here.

from unittest.mock import patch
from django.utils.timezone import now
from app.models import CustomUser
from notification.service import *
from content.models import Content
from category.models import Category
from suscription.models import Suscription
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationServiceTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="password123"
        )

        # Create a test category
        self.category = Category.objects.create(
            name="Test Category",
            description="Description for testing",
            type=Category.TypeChoices.public,
            is_active=True,
            is_moderated=True
        )

        # Create a test content related to the user and category
        self.content = Content.objects.create(
            title="Test Content",
            summary="Summary for testing",
            category=self.category,
            autor=self.user,
            state=Content.StateChoices.draft,
            date_expire=now()  # Now should be resolved correctly
        )

        # Create a test subscription
        self.suscription = Suscription.objects.create(
            user=self.user,
            category=self.category,
            state=Suscription.SuscriptionState.active
        )

    @patch("notification.tasks.send_notification_task.delay")
    def test_change_state(self, mock_send_notification_task):
        # Probar que changeState envía la notificación correcta
        changeState([self.user.email], self.content, "draft")

        # Verificar que send_notification_task fue llamado con los argumentos correctos
        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Cambio de estado")  # Asunto del correo
        self.assertIn("Tu contenido Test Content ha cambiado de estado", args[2]["message"])

    @patch("notification.tasks.send_notification_task.delay")
    def test_change_role(self, mock_send_notification_task):
        # Crear grupo simulado
        from django.contrib.auth.models import Group
        group = Group.objects.create(name="Test Group")

        changeRole(self.user, [group], added=True)

        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Has sido añadido a un rol.")
        self.assertIn("Test Group", args[2]["message"])

    @patch("notification.tasks.send_notification_task.delay")
    def test_welcome_user(self, mock_send_notification_task):
        welcomeUser(self.user)

        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "¡Bienvenido a nuestra aplicación!")
        self.assertIn("Gracias por registrarte en nuestra aplicación", args[2]["message"])

    @patch("notification.tasks.send_notification_task.delay")
    def test_expire_content(self, mock_send_notification_task):
        expire_content(self.user, self.content)

        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Contenido vencido")
        self.assertIn("Tu contenido Test Content ha expirado", args[2]["message"])

    @patch("notification.tasks.send_notification_task.delay")
    def test_payment_success(self, mock_send_notification_task):
        # Create a fake invoice structure
        class FakeInvoice:
            amount_paid = 1000
            currency = "USD"

            # Nested structure to simulate lines and period end
            class FakeLine:
                class FakePeriod:
                    end = 1672531199  # Simulate a timestamp for end

                period = FakePeriod()

            lines = type("Lines", (), {"data": [FakeLine()]})
            status_transitions = type("Transitions", (), {"paid_at": 1672531199})

        invoice = FakeInvoice()

        payment_success(self.user, self.category, invoice)

        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Pago exitoso")
        self.assertIn("tu pago por la categoría Test Category ha sido procesado exitosamente", args[2]["message"])


    @patch("notification.tasks.send_notification_task.delay")
    def test_payment_failed(self, mock_send_notification_task):
        # Crear factura simulada
        class FakeInvoice:
            amount_due = 1000
            currency = "USD"
            effective_at = 1672531199

        invoice = FakeInvoice()
        payment_failed(self.user, self.category, invoice)

        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Pago fallido")
        self.assertIn("Lamentamos informarte que el intento de pago de tu suscripción", args[2]["message"])

    @patch("notification.tasks.send_notification_task.delay")
    def test_subscription_cancelled(self, mock_send_notification_task):
        subscription_cancelled(self.user, self.category)

        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Suscripción cancelada")
        self.assertIn("tu suscripción a la categoría Test Category ha sido cancelada", args[2]["message"])



