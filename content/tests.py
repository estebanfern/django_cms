import json
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from app.models import CustomUser
from app.signals import cache_previous_user, post_save_user_handler
from category.models import Category
from category.signals import cache_previous_category, post_save_category_handler, cache_category_before_delete, handle_category_after_delete
from content.forms import ContentForm
from content.models import Content
from unittest.mock import patch

class ContentCreateViewTest(TestCase):
    """
    Tests para la vista de creación de contenido (`ContentCreateView`).

    Hereda de:
        - TestCase: Clase base para escribir tests unitarios en Django.

    Atributos:
        user (CustomUser): Usuario de prueba con permisos para crear contenido.
        category (Category): Categoría de prueba para asociar al contenido.

    Métodos:
        setUp: Configura los datos necesarios para los tests, incluyendo la creación de un usuario con permisos, una categoría y la sesión de usuario.
        test_access_create_content_with_permission: Verifica que un usuario con los permisos adecuados puede acceder a la vista de creación de contenido.
        test_access_create_content_without_permission: Verifica que un usuario sin los permisos adecuados recibe un error 403 al intentar acceder a la vista de creación de contenido.
        test_form_valid_content_creation: Verifica que un formulario válido permite crear contenido y redirige correctamente.
        test_form_invalid_content_creation: Verifica que un formulario con datos inválidos muestra el formulario de nuevo con errores indicados.
    """

    def setUp(self):
        """
        Configura los datos necesarios para los tests.

        Lógica:
            - Crea un usuario de prueba con un permiso específico para crear contenido.
            - Asigna el permiso al usuario y lo inicia sesión para los tests.
            - Crea una categoría de prueba para asociar con el contenido.

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

        # Obtener los permisos necesarios
        perm1 = Permission.objects.get(codename='create_content')

        # Asignar múltiples permisos al usuario
        self.user.user_permissions.add(perm1)

        # Iniciar sesión con el usuario para los tests
        self.client.login(email='testuser@example.com', password='testpassword123')

        # Crear una categoría para los tests
        self.category = Category.objects.create(name='Test Category')

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    def test_access_create_content_with_permission(self):
        """
        Verifica que un usuario autenticado con permiso adecuado puede acceder a la vista de creación de contenido.

        Lógica:
            - Intenta acceder a la URL de creación de contenido con un usuario que tiene permisos.
            - Verifica que la respuesta tiene un código de estado 200.
            - Verifica que se utiliza la plantilla correcta para la vista.
        """
        url = reverse('content-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Se esperaba un código de estado 200 para un usuario con permisos.")
        self.assertTemplateUsed(response, 'content/content_form.html', "Se esperaba usar la plantilla 'content/content_form.html'.")

    def test_access_create_content_without_permission(self):
        """
        Verifica que un usuario sin permiso para crear contenido recibe un error 403 al intentar acceder a la vista de creación.

        Lógica:
            - Crea un nuevo usuario sin permisos.
            - Intenta acceder a la URL de creación de contenido con el usuario sin permisos.
            - Verifica que la respuesta tiene un código de estado 403.

        """
        # Crear un nuevo usuario sin permisos
        new_user = CustomUser.objects.create_user(
            email='newuser@example.com',
            name='New User',
            password='12345'
        )
        self.client.login(username='newuser@example.com', password='12345')

        url = reverse('content-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403, "Se esperaba un error 403 para un usuario sin permisos.")

    def test_form_valid_content_creation(self):
        """
        Verifica que un usuario con permisos puede crear contenido válido y es redirigido correctamente.

        Lógica:
            - Envía un formulario con datos válidos a la URL de creación de contenido.
            - Verifica que la respuesta es una redirección (código 302).
            - Verifica que el contenido creado existe en la base de datos.
        """
        url = reverse('content-create')
        response = self.client.post(url, {
            'title': 'Test Content',
            'summary': 'Summary of the test content',
            'category': self.category.id,
            'autor': self.user.id,
            'date_expire': timezone.now() + timezone.timedelta(days=1),
            'content': 'This is a test content',
            'tags': 'test, content',
            'state': 'draft'
        })
        self.assertEqual(response.status_code, 302, "Se esperaba una redirección (código 302) tras la creación de contenido válido.")
        self.assertTrue(Content.objects.filter(title='Test Content').exists(), "El contenido creado no se encuentra en la base de datos.")

    def test_form_invalid_content_creation(self):
        """
        Verifica que si el formulario para crear contenido tiene datos inválidos, se muestra el formulario de nuevo con errores.

        Lógica:
            - Envía un formulario con un campo obligatorio vacío a la URL de creación de contenido.
            - Verifica que la respuesta tiene un código de estado 200, indicando que el formulario se muestra de nuevo.
            - Verifica que se muestra un error de formulario para el campo faltante.
        """
        url = reverse('content-create')
        response = self.client.post(url, {
            'title': '',  # Título vacío debería ser inválido
            'summary': 'Summary of the test content',
            'category': self.category.id,
            'autor': self.user.id,
            'date_expire': timezone.now() + timezone.timedelta(days=1),
            'content': 'This is a test content',
            'tags': 'test, content',
            'state': 'draft'
        })
        self.assertEqual(response.status_code, 200, "Se esperaba el código de estado 200 cuando el formulario es inválido.")
        self.assertFormError(response, 'form', 'title', 'Este campo es obligatorio.', "Se esperaba un error de formulario para el campo 'title'.")


class ContentUpdateViewTest(TestCase):
    """
    Tests para la vista de actualización de contenido (`ContentUpdateView`).

    Hereda de:
        - TestCase: Clase base para escribir tests unitarios en Django.

    Atributos:
        user (CustomUser): Usuario de prueba con permisos para actualizar contenido.
        category (Category): Categoría de prueba para asociar al contenido.
        content (Content): Contenido de prueba existente para actualizar.

    Métodos:
        setUp: Configura los datos necesarios para los tests, incluyendo la creación de un usuario con permisos, una categoría, y un contenido existente.
        test_update_content_view: Verifica que un usuario con los permisos adecuados puede acceder a la vista de actualización de contenido.
        test_form_valid_content_update: Verifica que un formulario válido permite actualizar el contenido y redirige correctamente.
        test_form_invalid_content_update: Verifica que un formulario con datos inválidos muestra el formulario de nuevo con errores indicados.
    """

    def setUp(self):
        """
        Configura los datos necesarios para los tests.

        Lógica:
            - Crea un usuario de prueba con un permiso específico para crear contenido.
            - Asigna el permiso al usuario y lo inicia sesión para los tests.
            - Crea una categoría de prueba.
            - Crea un contenido de prueba asociado al usuario y la categoría.
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

        # Obtener los permisos necesarios
        perm1 = Permission.objects.get(codename='create_content')

        # Asignar múltiples permisos al usuario
        self.user.user_permissions.add(perm1)

        # Iniciar sesión con el usuario para los tests
        self.client.login(email='testuser@example.com', password='testpassword123')
        self.category = Category.objects.create(name='Test Category')
        self.content = Content.objects.create(
            title='Existing Content',
            summary='Summary of existing content',
            category=self.category,
            autor=self.user,
            state='draft',
            content='Existing content',
        )

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    def test_update_content_view(self):
        """
        Verifica que un usuario con permiso puede acceder a la vista de actualización de contenido.

        Lógica:
            - Intenta acceder a la URL de actualización del contenido con un usuario que tiene permisos.
            - Verifica que la respuesta tiene un código de estado 200.
            - Verifica que se utiliza la plantilla correcta para la vista.
        """
        url = reverse('content-update', args=[self.content.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Se esperaba un código de estado 200 para un usuario con permisos.")
        self.assertTemplateUsed(response, 'content/content_form.html', "Se esperaba usar la plantilla 'content/content_form.html'.")

    def test_form_valid_content_update(self):
        """
        Verifica que un usuario con permisos puede actualizar el contenido correctamente y es redirigido después de la actualización.

        Lógica:
            - Envía un formulario con datos válidos a la URL de actualización del contenido.
            - Verifica que la respuesta es una redirección (código 302).
            - Actualiza la instancia de contenido desde la base de datos y verifica que los cambios se aplicaron correctamente.
        """
        url = reverse('content-update', args=[self.content.pk])
        response = self.client.post(url, {
            'title': 'Updated Content',
            'summary': 'Updated summary',
            'category': self.category.id,
            'autor': self.user.id,
            'date_expire': timezone.now() + timezone.timedelta(days=2),
            'content': 'Updated content',
            'tags': 'updated, content',
            'state': 'publish'
        })
        self.assertEqual(response.status_code, 302, "Se esperaba una redirección (código 302) tras la actualización de contenido válido.")
        self.content.refresh_from_db()
        self.assertEqual(self.content.title, 'Updated Content', "El título del contenido no se actualizó correctamente.")

    def test_form_invalid_content_update(self):
        """
        Verifica que si el formulario para actualizar contenido tiene datos inválidos, se muestra el formulario de nuevo con errores.

        Lógica:
            - Envía un formulario con un campo obligatorio vacío a la URL de actualización de contenido.
            - Verifica que la respuesta tiene un código de estado 200, indicando que el formulario se muestra de nuevo.
            - Verifica que se muestra un error de formulario para el campo faltante.

        """
        url = reverse('content-update', args=[self.content.pk])
        response = self.client.post(url, {
            'title': '',  # Título vacío debería ser inválido
            'summary': 'Updated summary',
            'category': self.category.id,
            'autor': self.user.id,
            'date_expire': timezone.now() + timezone.timedelta(days=2),
            'content': 'Updated content',
            'tags': 'updated, content',
            'state': 'publish'
        })
        self.assertEqual(response.status_code, 200, "Se esperaba el código de estado 200 cuando el formulario es inválido.")
        self.assertFormError(response, 'form', 'title', 'Este campo es obligatorio.', "Se esperaba un error de formulario para el campo 'title'.")

class ContentUpdateViewEditorTest(TestCase):
    """
    Tests para la vista de actualización de contenido por un editor (`ContentUpdateView`).

    Hereda de:
        - TestCase: Clase base para escribir tests unitarios en Django.

    Atributos:
        editor (CustomUser): Usuario de prueba con permisos de edición de contenido.
        category (Category): Categoría de prueba para asociar al contenido.
        content (Content): Contenido de prueba en estado de revisión para actualizar.

    Métodos:
        setUp: Configura los datos necesarios para los tests, incluyendo la creación de un usuario con permisos de editor, una categoría y un contenido en estado de revisión.
        test_update_content_view_for_editor: Verifica que un editor puede acceder a la vista de actualización de contenido en estado revisión.
        test_editor_cannot_update_other_fields: Verifica que un editor no puede actualizar campos distintos a 'content' en estado 'revision'.
    """

    def setUp(self):
        """
        Configura los datos necesarios para los tests.

        Lógica:
            - Crea un usuario de prueba con permiso de editor.
            - Asigna el permiso de edición al usuario y lo inicia sesión para los tests.
            - Crea una categoría de prueba.
            - Crea un contenido de prueba en estado de revisión asociado al usuario editor.
        """
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)

        # Crear un usuario con permiso de editor
        self.editor = get_user_model().objects.create_user(
            email='editor@example.com',
            name='Editor User',
            password='testpassword123'
        )

        # Obtener los permisos necesarios
        perm1 = Permission.objects.get(codename='edit_content')

        # Asignar permisos de edición al usuario
        self.editor.user_permissions.add(perm1)

        # Crear una categoría y contenido en estado de revisión
        self.category = Category.objects.create(name='Test Category')
        self.content = Content.objects.create(
            title='Content in Revision',
            summary='Content summary in revision state',
            category=self.category,
            autor=self.editor,  # Puede ser el autor u otro usuario, según el caso
            state='revision',  # Estado revisión
            content='Original content text',
        )

        # Iniciar sesión con el usuario editor para las pruebas
        self.client.login(email='editor@example.com', password='testpassword123')

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    def test_update_content_view_for_editor(self):
        """
        Verifica que un editor puede acceder a la vista de actualización de contenido en estado revisión.

        Lógica:
            - Intenta acceder a la URL de actualización del contenido con un usuario que tiene permisos de edición.
            - Verifica que la respuesta tiene un código de estado 200.
            - Verifica que se utiliza la plantilla correcta para la vista.
        """
        url = reverse('content-update', args=[self.content.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Se esperaba un código de estado 200 para un editor con permisos.")
        self.assertTemplateUsed(response, 'content/content_form.html', "Se esperaba usar la plantilla 'content/content_form.html'.")

    # def test_editor_can_update_content_in_revision(self):
    #     """
    #     Verifica que un editor puede actualizar el contenido en estado 'revision'.
    #     """
    #     url = reverse('content-update', args=[self.content.pk])
    #     response = self.client.post(url, {
    #         'content': 'Updated content text by editor',
    #         'change_reason': 'Fixed typos and updated the content for clarity',
    #         'category': self.category.id,  # Este campo es necesario en el formulario
    #     })

    #     self.assertEqual(response.status_code, 302, "Se esperaba una redirección (código 302) tras la actualización por el editor.")
    #     self.content.refresh_from_db()

    #     # Verificamos que solo el campo 'content' ha sido actualizado
    #     self.assertEqual(self.content.content, 'Updated content text by editor', "El contenido no fue actualizado correctamente por el editor.")
    #     self.assertEqual(self.content.title, 'Content in Revision', "El editor no debería haber cambiado el título.")
    #     self.assertEqual(self.content.state, 'revision', "El estado del contenido no debería haber cambiado.")

    #     # Verifica que la razón del cambio ha sido almacenada correctamente
    #     history_entry = self.content.history.latest('history_date')
    #     self.assertEqual(history_entry.history_change_reason, 'Fixed typos and updated the content for clarity', "La razón del cambio no fue registrada correctamente.")

    def test_editor_cannot_update_other_fields(self):
        """
        Verifica que un editor no puede actualizar campos distintos a 'content' en estado 'revision'.

        Lógica:
            - Envía un formulario con campos adicionales modificados (como título y resumen) junto con el contenido.
            - Verifica que la respuesta es una redirección (código 302).
            - Actualiza la instancia de contenido desde la base de datos y verifica que solo el campo 'content' ha sido actualizado.
            - Verifica que los campos 'title' y 'summary' no han cambiado, asegurando que el editor no pudo modificarlos.
        """
        url = reverse('content-update', args=[self.content.pk])
        response = self.client.post(url, {
            'title': 'Title changed by editor',  # El editor no debería poder cambiar el título
            'summary': 'Summary changed by editor',
            'category': self.category.id,
            'content': 'Updated content text by editor',
            'change_reason': 'Changed content and tried to change title/summary',
        })

        self.assertEqual(response.status_code, 302, "Se esperaba una redirección tras la actualización.")
        self.content.refresh_from_db()

        # Solo el campo 'content' debería haber cambiado
        self.assertEqual(self.content.content, 'Updated content text by editor', "El contenido no fue actualizado correctamente.")
        self.assertEqual(self.content.title, 'Content in Revision', "El editor no debería haber podido cambiar el título.")
        self.assertEqual(self.content.summary, 'Content summary in revision state', "El editor no debería haber podido cambiar el resumen.")


class ContentFormTest(TestCase):
    """
    Tests para el formulario de creación y actualización de contenido (`ContentForm`).

    Hereda de:
        - TestCase: Clase base para escribir tests unitarios en Django.

    Atributos:
        user (CustomUser): Usuario de prueba.
        category (Category): Categoría de prueba para asociar al contenido.

    Métodos:
        setUp: Configura los datos necesarios para los tests, incluyendo la creación de un usuario y una categoría de prueba.
        test_content_form_creation_valid: Verifica que el formulario de creación de contenido es válido con los datos correctos.
        test_form_disabled_fields_for_editor: Verifica que los campos que no deben ser modificados están deshabilitados cuando el contenido está en estado de revisión.
    """

    def setUp(self):
        """
        Configura los datos necesarios para los tests.

        Lógica:
            - Crea un usuario de prueba con un correo electrónico, nombre y contraseña.
            - Crea una categoría de prueba para asociar al contenido en los tests.
        """
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)

        # Crear usuario y categoría de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )
        self.category = Category.objects.create(name='Test Category')

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    def test_content_form_creation_valid(self):
        """
        Verifica que el formulario de creación de contenido es válido con los datos correctos.

        Lógica:
            - Define datos válidos para el formulario de contenido.
            - Crea una instancia del formulario con los datos proporcionados.
            - Verifica que el formulario es válido usando `assertTrue`.

        """
        form_data = {
            'title': 'New Content',
            'summary': 'This is a summary for new content',
            'category': self.category.id,
            'date_published': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
            'date_expire': (timezone.now() + timezone.timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
            'content': 'This is the body of the new content',
            'tags': 'test, content',
        }
        form = ContentForm(data=form_data)
        self.assertTrue(form.is_valid(), "El formulario debería ser válido con los datos correctos.")


    def test_form_disabled_fields_for_editor(self):
        """
        Verifica que los campos que no deben ser modificados están deshabilitados cuando el contenido está en estado de revisión.

        Lógica:
            - Crea un contenido de prueba en estado de revisión.
            - Inicializa el formulario `ContentForm` con la instancia de contenido en estado de revisión.
            - Verifica que los campos 'title', 'date_published' y 'date_expire' están deshabilitados en el formulario para los editores.
        """
        content = Content.objects.create(
            title='Content in Revision',
            summary='Summary of content in revision',
            category=self.category,
            autor=self.user,
            state=Content.StateChoices.revision,
            content='Content body',
        )
        form = ContentForm(instance=content)
        self.assertIn('disabled', form.fields['title'].widget.attrs, "El campo 'title' debería estar deshabilitado.")
        self.assertIn('disabled', form.fields['date_published'].widget.attrs, "El campo 'date_published' debería estar deshabilitado.")
        self.assertIn('disabled', form.fields['date_expire'].widget.attrs, "El campo 'date_expire' debería estar deshabilitado.")


class ReactionTestCase(TestCase):
    """
    Pruebas para la funcionalidad de like y dislike en el contenido.
    """

    def setUp(self):
        """
        Configura los datos necesarios para las pruebas, incluyendo un usuario y contenido de prueba.
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

        # Iniciar sesión con el usuario
        self.client.login(email='testuser@example.com', password='testpassword123')

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    @patch('content.views.update_reactions.delay')  # Mock the Celery task
    def test_like_content(self, mock_update_reactions):
        """
        Asegura que un usuario pueda dar like a un contenido y se registre el like.
        """
        url = reverse('like_content', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el usuario ha dado like al contenido
        self.assertTrue(self.content.likes.filter(id=self.user.id).exists())

        # Verificar que la tarea Celery fue llamada una vez
        mock_update_reactions.assert_called_once_with(self.content.id)

    @patch('content.views.update_reactions.delay')  # Mock the Celery task
    def test_dislike_content(self, mock_update_reactions):
        """
        Asegura que un usuario pueda dar dislike a un contenido y se registre el dislike.
        """
        url = reverse('dislike_content', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el usuario ha dado dislike al contenido
        self.assertTrue(self.content.dislikes.filter(id=self.user.id).exists())

        # Verificar que la tarea Celery fue llamada una vez
        mock_update_reactions.assert_called_once_with(self.content.id)

    @patch('content.views.update_reactions.delay')  # Mock the Celery task
    def test_remove_like(self, mock_update_reactions):
        """
        Asegura que un usuario pueda quitar un like de un contenido.
        """
        # Primero, dar like al contenido
        self.content.likes.add(self.user)

        # Ahora, quitar el like
        url = reverse('like_content', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el like ha sido eliminado
        self.assertFalse(self.content.likes.filter(id=self.user.id).exists())

        # Verificar que la tarea Celery fue llamada una vez
        mock_update_reactions.assert_called_once_with(self.content.id)

    @patch('content.views.update_reactions.delay')  # Mock the Celery task
    def test_remove_dislike(self, mock_update_reactions):
        """
        Asegura que un usuario pueda quitar un dislike de un contenido.
        """
        # Primero, dar dislike al contenido
        self.content.dislikes.add(self.user)

        # Ahora, quitar el dislike
        url = reverse('dislike_content', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el dislike ha sido eliminado
        self.assertFalse(self.content.dislikes.filter(id=self.user.id).exists())

        # Verificar que la tarea Celery fue llamada una vez
        mock_update_reactions.assert_called_once_with(self.content.id)

    @patch('content.views.update_reactions.delay')  # Mock the Celery task
    def test_like_then_dislike(self, mock_update_reactions):
        """
        Asegura que dar like a un contenido elimina un dislike existente.
        """
        # Primero, dar dislike al contenido
        self.content.dislikes.add(self.user)

        # Ahora, dar like al contenido
        url = reverse('like_content', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el dislike ha sido eliminado y el contenido tiene like
        self.assertFalse(self.content.dislikes.filter(id=self.user.id).exists())
        self.assertTrue(self.content.likes.filter(id=self.user.id).exists())

        # Verificar que la tarea Celery fue llamada una vez
        mock_update_reactions.assert_called_once_with(self.content.id)

    @patch('content.views.update_reactions.delay')  # Mock the Celery task
    def test_dislike_then_like(self, mock_update_reactions):
        """
        Asegura que dar dislike a un contenido elimina un like existente.
        """
        # Primero, dar like al contenido
        self.content.likes.add(self.user)

        # Ahora, dar dislike al contenido
        url = reverse('dislike_content', args=[self.content.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Verificar que el like ha sido eliminado y el contenido tiene dislike
        self.assertFalse(self.content.likes.filter(id=self.user.id).exists())
        self.assertTrue(self.content.dislikes.filter(id=self.user.id).exists())

        # Verificar que la tarea Celery fue llamada una vez
        mock_update_reactions.assert_called_once_with(self.content.id)


class KanbanBoardTest(TestCase):
    def setUp(self):
        pre_save.disconnect(cache_previous_user, sender=CustomUser)
        post_save.disconnect(post_save_user_handler, sender=CustomUser)
        pre_save.disconnect(cache_previous_category, sender=Category)
        post_save.disconnect(post_save_category_handler, sender=Category)
        pre_delete.disconnect(cache_category_before_delete, sender=Category)
        post_delete.disconnect(handle_category_after_delete, sender=Category)

        self.user = CustomUser.objects.create_user(email='user@mail.com', password='testpassword',
                                                   name='Test User')
        self.user_creator = CustomUser.objects.create_user(email='creator@example.com', password='password123',
                                                           name='Creator User')
        self.user_editor = CustomUser.objects.create_user(email='editor@example.com', password='password123',
                                                          name='Editor User')
        self.user_publisher = CustomUser.objects.create_user(email='publisher@example.com', password='password123',
                                                             name='Publisher User')
        self.user_is_active_editor = CustomUser.objects.create_user(email='activeeditor@example.com', password='password123',
                                                                    name='IsActive Editor')

        # Asignar permisos
        self.user_creator.user_permissions.add(Permission.objects.get(codename='create_content'))
        self.user_editor.user_permissions.add(Permission.objects.get(codename='edit_content'))
        self.user_publisher.user_permissions.add(Permission.objects.get(codename='publish_content'))
        self.user_is_active_editor.user_permissions.add(Permission.objects.get(codename='edit_is_active'))

        # Crear categorías moderadas y no moderadas
        self.category_moderated = Category.objects.create(name='Moderated Category', is_moderated=True)
        self.category_unmoderated = Category.objects.create(name='Unmoderated Category', is_moderated=False)

        # Crear contenido de prueba
        self.content_draft = Content.objects.create(
            title="Draft Content",
            summary="Content in draft state",
            category=self.category_unmoderated,
            autor=self.user_creator,
            state='draft',
            content="Sample content",
        )
        self.content_inactive = Content.objects.create(
            title="Inactive Content",
            summary="Content in inactive state",
            category=self.category_unmoderated,
            autor=self.user_creator,
            state='inactive',
            date_published=timezone.now() - timezone.timedelta(days=2),
            date_expire=timezone.now() + timezone.timedelta(days=1)
        )
        self.content_other = Content.objects.create(
            title="Other User Content",
            summary="Content by another user",
            category=self.category_unmoderated,
            autor=self.user,
            state='draft',
            content="Sample content",
        )
        self.expired_content = Content.objects.create(
            title="Expired Content",
            summary="Content that has expired",
            category=self.category_unmoderated,
            autor=self.user_creator,
            state='inactive',
            date_published=timezone.now() - timezone.timedelta(days=2),
            date_expire=timezone.now() - timezone.timedelta(days=1),
        )

    def tearDown(self):
        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    # Pruebas para la vista kanban_board
    def test_user_without_permissions(self):
        # Iniciar sesión con un usuario sin permisos
        self.client.login(email='user@mail.com', password='testpassword')

        # Realizamos una solicitud al tablero Kanban
        response = self.client.get(reverse('kanban_board'))

        # Verificar si el usuario es redirigido a la página de login
        self.assertEqual(response.status_code, 403,
                         "El usuario sin permisos no debería poder acceder al tablero Kanban.")

    def test_user_with_create_content_permission(self):
        self.user.user_permissions.add(Permission.objects.get(codename='create_content'))
        self.client.login(email='user@mail.com', password='testpassword')

        response = self.client.get(reverse('kanban_board'))

        # Verificamos que el usuario tenga acceso al tablero
        self.assertEqual(response.status_code, 200,
                         "El usuario con permiso de creación no pudo acceder al tablero Kanban.")

        # Verificamos que se muestren los contenidos correctamente
        self.assertIn('Borrador', response.context['contents'],
                      "El contenido en estado 'Borrador' no aparece en el tablero.")

    def test_user_with_edit_content_permission(self):
        self.user.user_permissions.add(Permission.objects.get(codename='edit_content'))
        self.client.login(email='user@mail.com', password='testpassword')

        response = self.client.get(reverse('kanban_board'))

        # Verificamos que el usuario tenga acceso al tablero
        self.assertEqual(response.status_code, 200,
                         "El usuario con permisos de edición no pudo acceder al tablero.")

        # Verificamos que se muestren los contenidos correctamente
        self.assertIn('Edicion', response.context['contents'],
                      "El contenido en estado 'Borrador' no aparece en el tablero.")

    def test_user_with_publish_content_permission(self):
        self.user.user_permissions.add(Permission.objects.get(codename='publish_content'))
        self.client.login(email='user@mail.com', password='testpassword')

        response = self.client.get(reverse('kanban_board'))

        # Verificamos que el usuario tenga acceso al tablero
        self.assertEqual(response.status_code, 200,
                         "El usuario con permisos de publicador no pudo acceder al tablero.")

        # Verificamos que se muestren los contenidos correctamente
        self.assertIn('Publicado', response.context['contents'],
                      "El contenido en estado 'Publicado' no aparece en el tablero.")

    def test_user_with_edit_is_active_permission(self):
        self.user.user_permissions.add(Permission.objects.get(codename='edit_is_active'))
        self.client.login(email='user@mail.com', password='testpassword')

        response = self.client.get(reverse('kanban_board'))

        # Verificamos que el usuario tenga acceso al tablero
        self.assertEqual(response.status_code, 200,
                         "El usuario con permisos de administrador no pudo acceder al tablero.")

        # Verificamos que se muestren los contenidos correctamente
        self.assertIn('Publicado', response.context['contents'],
                      "El contenido en estado 'Publicado' no aparece en el tablero.")


    # Pruebas para la API update_content_state
    def test_invalid_http_method(self):
        category = Category.objects.create(name='Test Category')
        content = Content.objects.create(
            title='Existing Content',
            summary='Summary of existing content',
            category=category,
            autor=self.user,
            state='draft',
            content='Existing content',
        )
        self.client.login(email='user@mail.com', password='testpassword')

        response = self.client.get(reverse('update_content_state', args=[content.id]))

        # Verificamos que el método GET no esté permitido
        self.assertEqual(response.status_code, 405, "El método GET no debería estar permitido en la API.")
        self.assertEqual(response.json()['message'], 'Método no permitido.',
                         "El mensaje de error para el método GET no es el esperado.")

    # Movimiento de "borrador" a "revisión" del propio contenido
    def test_creator_move_draft_to_revision(self):
        self.client.login(email='creator@example.com', password='password123')
        data = {'state': 'revision'}  # Enviamos los datos como JSON
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'revision',
                         "El creador debería poder mover su contenido de borrador a revisión.")

    # Movimiento de "borrador" a "publicado" (categoría no moderada)
    def test_creator_move_draft_to_publish_unmoderated(self):
        self.client.login(email='creator@example.com', password='password123')
        data = {'state': 'publish'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'publish',
                         "El creador debería poder mover su contenido de borrador a publicado si la categoría no está moderada.")

    # Movimiento de "publicado" a "inactivo" por el creador (su propio contenido)
    def test_creator_move_publish_to_inactive(self):
        # Cambiar el contenido a publicado primero
        self.content_draft.state = 'publish'
        self.content_draft.save()

        self.client.login(email='creator@example.com', password='password123')
        data = {'state': 'inactive'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'inactive',
                         "El creador debería poder mover su contenido de publicado a inactivo.")

    # El creador no puede mover un contenido que no es suyo
    def test_creator_cannot_move_other_user_content(self):
        self.client.login(email='creator@example.com', password='password123')
        data = {'state': 'revision'}
        self.client.post(
            reverse('update_content_state', args=[self.content_other.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_other.refresh_from_db()
        self.assertNotEqual(self.content_other.state, 'revision',
                            "El creador no debería poder cambiar el estado de un contenido que no es suyo.")


    def test_editor_move_revision_to_to_publish(self):
        # Cambiar el contenido a revisión primero
        self.content_draft.state = 'revision'
        self.content_draft.save()

        self.client.login(email='editor@example.com', password='password123')
        data = {'state': 'to_publish'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'to_publish',
                         "El editor debería poder mover contenido de revisión a a publicar.")

    def test_editor_move_revision_to_draft(self):
        # Cambiar el contenido a revisión primero
        self.content_draft.state = 'revision'
        self.content_draft.save()

        self.client.login(email='editor@example.com', password='password123')
        data = {'state': 'draft'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'draft',
                         "El editor debería poder mover contenido de revisión a borrador.")

    def test_publisher_move_to_publish_to_publish(self):
        # Cambiar el contenido a "a publicar"
        self.content_draft.state = 'to_publish'
        self.content_draft.save()

        self.client.login(email='publisher@example.com', password='password123')
        data = {'state': 'publish'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'publish',
                         "El publicador debería poder mover contenido de a publicar a publicado.")

    def test_publisher_move_to_publish_to_revision(self):
        # Cambiar el contenido a "a publicar" primero
        self.content_draft.state = 'to_publish'
        self.content_draft.save()

        self.client.login(email='publisher@example.com', password='password123')
        data = {'state': 'revision'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'revision',
                         "El publicador debería poder mover contenido de a publicar a revisión.")

    def test_is_active_editor_move_publish_to_inactive(self):
        # Cambiar el contenido a publicado
        self.content_draft.state = 'publish'
        self.content_draft.save()

        self.client.login(email='activeeditor@example.com', password='password123')
        data = {'state': 'inactive'}
        self.client.post(
            reverse('update_content_state', args=[self.content_draft.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_draft.refresh_from_db()
        self.assertEqual(self.content_draft.state, 'inactive',
                         "El usuario con permiso de edit_is_active debería poder mover contenido de publicado a inactivo.")


    def test_creator_move_inactive_to_publish(self):
        # El contenido en estado inactivo y no expirado
        self.client.login(email='creator@example.com', password='password123')
        data = {'state': 'publish'}
        self.client.post(
            reverse('update_content_state', args=[self.content_inactive.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.content_inactive.refresh_from_db()
        self.assertEqual(self.content_inactive.state, 'publish',
                         "El creador debería poder mover contenido inactivo a publicado si no ha expirado.")

    def test_creator_cannot_move_inactive_to_publish_expired(self):
        self.client.login(email='creator@example.com', password='password123')
        data = {'state': 'publish'}

        # Intentar mover contenido inactivo a publicado (el contenido ha expirado)
        self.client.post(
            reverse('update_content_state', args=[self.expired_content.id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.expired_content.refresh_from_db()
        self.assertEqual(self.expired_content.state, 'inactive',
                         "El contenido expirado no debería poder moverse de inactivo a publicado.")
