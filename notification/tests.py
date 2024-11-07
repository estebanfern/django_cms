from django.test import TestCase
from unittest.mock import patch
from django.utils.timezone import now
from app.models import CustomUser
from notification.service import *
from content.models import Content
from category.models import Category
from suscription.models import Suscription
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from app.signals import cache_previous_user, post_save_user_handler
from category.signals import cache_previous_category, post_save_category_handler, cache_category_before_delete, handle_category_after_delete

User = get_user_model()

class NotificationServiceTests(TestCase):
    def setUp(self):
        # Disconnect signals to avoid side effects during tests
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)

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
            date_expire=now()
        )

        # Create a test subscription
        self.suscription = Suscription.objects.create(
            user=self.user,
            category=self.category,
            state=Suscription.SuscriptionState.active
        )

    def tearDown(self):
        # Reconnect signals after tests
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    @patch("notification.tasks.send_notification_task.delay")
    def test_change_state(self, mock_send_notification_task):
        changeState([self.user.email], self.content, "draft")
        mock_send_notification_task.assert_called_once()
        args, kwargs = mock_send_notification_task.call_args
        self.assertEqual(args[0], "Cambio de estado")
        self.assertIn("Tu contenido Test Content ha cambiado de estado", args[2]["message"])

    @patch("notification.tasks.send_notification_task.delay")
    def test_change_role(self, mock_send_notification_task):
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
        class FakeInvoice:
            amount_paid = 1000
            currency = "USD"
            class FakeLine:
                class FakePeriod:
                    end = 1672531199
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
