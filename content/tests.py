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
from content.forms import ContentForm, ReportForm
from content.models import Content, Report
from unittest.mock import patch

class ContentCreateViewTest(TestCase):
    """
    Clase de pruebas para la vista de creación de contenido (`ContentCreateView`).

    Prueba el acceso y las funcionalidades de creación de contenido, verificando permisos, validaciones del formulario
    y comportamientos esperados en la vista.

    """

    def setUp(self):
        """
        Configura el entorno necesario para los tests de `ContentCreateView`.

        Crea un usuario con permisos, una categoría de prueba, y establece la sesión del usuario.
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
        """
        Restablece las conexiones de señales después de cada test.
        """

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
    Clase de pruebas para la vista de actualización de contenido (`ContentUpdateView`).

    Métodos:
        - setUp: Configura los datos iniciales necesarios para las pruebas.
        - tearDown: Restaura los estados después de las pruebas.
        - test_update_content_view: Verifica que un usuario con permisos puede acceder a la vista de actualización.
        - test_form_valid_content_update: Verifica que un formulario válido permite actualizar el contenido.
        - test_form_invalid_content_update: Verifica que un formulario inválido muestra errores correctamente.
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
        """
        Restaura los estados del entorno después de cada prueba.

        Acciones:
            - Reconecta señales relacionadas.
            - Llama al metodo `tearDown` de la clase padre.
        """

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

    Propósito:
        Verificar que los editores puedan actualizar el campo 'content' de un contenido en estado de revisión,
        pero no otros campos como 'title' o 'summary'.

    :ivar editor: Usuario de prueba con permisos de edición de contenido.
    :type editor: CustomUser
    :ivar category: Categoría de prueba asociada al contenido.
    :type category: Category
    :ivar content: Contenido de prueba en estado de revisión para actualizar.
    :type content: Content

    Metodos:
        - :meth:`setUp`: Configura los datos necesarios para las pruebas, incluyendo la creación de un usuario con permisos,
          una categoría y un contenido existente en estado de revisión.
        - :meth:`tearDown`: Restaura las señales desconectadas y limpia el entorno después de cada prueba.
        - :meth:`test_update_content_view_for_editor`: Verifica que un editor puede acceder a la vista de actualización de contenido en estado de revisión.
        - :meth:`test_editor_cannot_update_other_fields`: Verifica que un editor no puede modificar campos distintos a 'content' en estado de revisión.
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
        """
        Restaura las señales y el entorno después de cada prueba.

        Acciones:
            - Reconecta señales relacionadas.
            - Llama al método :meth:`tearDown` de la clase base.
        """

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

    Propósito:
        Validar el comportamiento del formulario `ContentForm` en diferentes escenarios, incluyendo la creación
        de contenido válido y la restricción de campos deshabilitados para editores.

    Atributos:
        :ivar user: Usuario de prueba utilizado en los tests.
        :type user: CustomUser
        :ivar category: Categoría de prueba utilizada en los tests.
        :type category: Category

    Métodos:
        - :meth:`setUp`: Configura los datos necesarios para las pruebas, incluyendo la creación de un usuario y una categoría.
        - :meth:`tearDown`: Restaura las señales y limpia el entorno después de cada prueba.
        - :meth:`test_content_form_creation_valid`: Verifica que el formulario es válido cuando se proporcionan datos correctos.
        - :meth:`test_form_disabled_fields_for_editor`: Verifica que ciertos campos están deshabilitados cuando el contenido está en estado de revisión.
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
        """
        Restaura las señales y el entorno después de cada prueba.

        Acciones:
            - Reconecta señales desconectadas durante la configuración inicial.
            - Llama al metodo :meth:`tearDown` de la clase base.
        """

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
    Tests para la funcionalidad de reacciones (like y dislike) en el contenido.

    Propósito:
        Validar que los usuarios puedan interactuar correctamente con la funcionalidad de reacciones,
        incluyendo dar like, dislike, y cambiar entre ambos estados.

    Atributos:
        :ivar user: Usuario de prueba utilizado en los tests.
        :type user: CustomUser
        :ivar category: Categoría de prueba asociada al contenido.
        :type category: Category
        :ivar content: Contenido de prueba sobre el que se prueban las reacciones.
        :type content: Content

    Métodos:
        - :meth:`setUp`: Configura los datos necesarios para los tests, incluyendo un usuario, una categoría y un contenido.
        - :meth:`tearDown`: Reconecta señales y limpia el entorno después de cada prueba.
        - :meth:`test_like_content`: Verifica que un usuario pueda dar like a un contenido.
        - :meth:`test_dislike_content`: Verifica que un usuario pueda dar dislike a un contenido.
        - :meth:`test_remove_like`: Verifica que un usuario pueda quitar un like de un contenido.
        - :meth:`test_remove_dislike`: Verifica que un usuario pueda quitar un dislike de un contenido.
        - :meth:`test_like_then_dislike`: Verifica que al dar like se elimine un dislike previamente registrado.
        - :meth:`test_dislike_then_like`: Verifica que al dar dislike se elimine un like previamente registrado.
    """

    def setUp(self):
        """
            Configura los datos necesarios para los tests, incluyendo un usuario y contenido de prueba.

            Lógica:
                - Desconecta señales para evitar que afecten los tests.
                - Crea un usuario de prueba.
                - Crea una categoría de prueba para asociar al contenido.
                - Crea un contenido de prueba asociado a la categoría y el usuario.
                - Inicia sesión con el usuario de prueba.
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
        """
        Restaura las señales después de la ejecución de cada test.

        Propósito:
            Asegurar que las señales desconectadas en :meth:`setUp` se reconecten correctamente para evitar efectos secundarios.

        Lógica:
            - Reconecta todas las señales relacionadas con los modelos `CustomUser` y `Category`.
            - Llama al metodo `tearDown` de la clase base para realizar limpieza adicional.

        :return: None
        """

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
        Verifica que un usuario pueda dar like a un contenido y se registre correctamente.

        Lógica:
            - Hace una petición GET a la vista de like para un contenido específico.
            - Verifica que la petición sea exitosa (status code 200).
            - Verifica que el usuario haya dado like al contenido.
            - Asegura que la tarea Celery `update_reactions` haya sido llamada una vez.
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
        Verifica que un usuario pueda dar dislike a un contenido y se registre correctamente.

        Lógica:
            - Hace una petición GET a la vista de dislike para un contenido específico.
            - Verifica que la petición sea exitosa (status code 200).
            - Verifica que el usuario haya dado dislike al contenido.
            - Asegura que la tarea Celery `update_reactions` haya sido llamada una vez.
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
        Verifica que un usuario pueda quitar un like de un contenido.

        Lógica:
            - Añade un like al contenido por parte del usuario.
            - Hace una petición GET a la vista de like nuevamente para quitar el like.
            - Verifica que la petición sea exitosa (status code 200).
            - Verifica que el like haya sido eliminado.
            - Asegura que la tarea Celery `update_reactions` haya sido llamada una vez.
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
        Verifica que un usuario pueda quitar un dislike de un contenido.

        Lógica:
            - Añade un dislike al contenido por parte del usuario.
            - Hace una petición GET a la vista de dislike nuevamente para quitar el dislike.
            - Verifica que la petición sea exitosa (status code 200).
            - Verifica que el dislike haya sido eliminado.
            - Asegura que la tarea Celery `update_reactions` haya sido llamada una vez.
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
        Verifica que al dar like a un contenido se elimine un dislike previamente registrado.

        Lógica:
            - Añade un dislike al contenido.
            - Hace una petición GET a la vista de like para cambiar el dislike por un like.
            - Verifica que el dislike haya sido eliminado y que se haya registrado el like.
            - Asegura que la tarea Celery `update_reactions` haya sido llamada una vez.
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
        Verifica que al dar dislike a un contenido se elimine un like previamente registrado.

        Lógica:
            - Añade un like al contenido.
            - Hace una petición GET a la vista de dislike para cambiar el like por un dislike.
            - Verifica que el like haya sido eliminado y que se haya registrado el dislike.
            - Asegura que la tarea Celery `update_reactions` haya sido llamada una vez.
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
    """
    Tests para la vista de tablero Kanban y la API de actualización de estado de contenido (`update_content_state`).

    Propósito:
        Validar los permisos y flujos de trabajo en el tablero Kanban, asegurando que los usuarios solo puedan realizar acciones
        según los permisos asignados y las reglas del negocio.

    Atributos:
        :ivar user: Usuario de prueba sin permisos específicos.
        :type user: CustomUser
        :ivar user_creator: Usuario con permiso para crear contenido.
        :type user_creator: CustomUser
        :ivar user_editor: Usuario con permiso para editar contenido.
        :type user_editor: CustomUser
        :ivar user_publisher: Usuario con permiso para publicar contenido.
        :type user_publisher: CustomUser
        :ivar user_is_active_editor: Usuario con permiso para cambiar el estado activo del contenido.
        :type user_is_active_editor: CustomUser
        :ivar category_moderated: Categoría de prueba que requiere moderación.
        :type category_moderated: Category
        :ivar category_unmoderated: Categoría de prueba sin necesidad de moderación.
        :type category_unmoderated: Category
        :ivar content_draft: Contenido de prueba en estado borrador.
        :type content_draft: Content
        :ivar content_inactive: Contenido de prueba en estado inactivo.
        :type content_inactive: Content
        :ivar content_other: Contenido creado por un usuario diferente al usuario creador.
        :type content_other: Content
        :ivar expired_content: Contenido que ha expirado su fecha de publicación.
        :type expired_content: Content

    Métodos:
        - :meth:`setUp`: Configura los datos necesarios para los tests, incluyendo usuarios, permisos, categorías y contenidos.
        - :meth:`tearDown`: Restaura las señales y limpia los datos después de cada prueba.
        - :meth:`test_user_without_permissions`: Verifica que un usuario sin permisos no pueda acceder al tablero Kanban.
        - :meth:`test_user_with_create_content_permission`: Verifica que un usuario con permiso de creación pueda acceder al tablero.
        - :meth:`test_user_with_edit_content_permission`: Verifica que un usuario con permiso de edición pueda acceder al tablero.
        - :meth:`test_user_with_publish_content_permission`: Verifica que un usuario con permiso de publicación pueda acceder al tablero.
        - :meth:`test_user_with_edit_is_active_permission`: Verifica que un usuario con permiso para editar el estado activo pueda acceder al tablero.
        - :meth:`test_invalid_http_method`: Verifica que la API `update_content_state` no permita el método GET.
        - :meth:`test_creator_move_draft_to_revision`: Verifica que un creador pueda mover su contenido de borrador a revisión.
        - :meth:`test_creator_move_draft_to_publish_unmoderated`: Verifica que un creador pueda publicar contenido en una categoría no moderada.
        - :meth:`test_creator_move_publish_to_inactive`: Verifica que un creador pueda mover su propio contenido de publicado a inactivo.
        - :meth:`test_creator_cannot_move_other_user_content`: Verifica que un creador no pueda cambiar el estado de un contenido que no le pertenece.
        - :meth:`test_editor_move_revision_to_to_publish`: Verifica que un editor pueda mover contenido de revisión a "a publicar".
        - :meth:`test_editor_move_revision_to_draft`: Verifica que un editor pueda mover contenido de revisión a borrador.
        - :meth:`test_publisher_move_to_publish_to_publish`: Verifica que un publicador pueda mover contenido de "a publicar" a publicado.
        - :meth:`test_publisher_move_to_publish_to_revision`: Verifica que un publicador pueda mover contenido de "a publicar" a revisión.
        - :meth:`test_is_active_editor_move_publish_to_inactive`: Verifica que un usuario con permiso `edit_is_active` pueda mover contenido de publicado a inactivo.
        - :meth:`test_creator_move_inactive_to_publish`: Verifica que un creador pueda mover contenido inactivo a publicado si no ha expirado.
        - :meth:`test_creator_cannot_move_inactive_to_publish_expired`: Verifica que un creador no pueda mover contenido expirado de inactivo a publicado.
    """

    def setUp(self):
        """
        Configura los datos necesarios para las pruebas.

        Lógica:
            - Desconecta señales para evitar efectos secundarios en los tests.
            - Crea usuarios con diferentes permisos (crear, editar, publicar y modificar estado activo).
            - Crea categorías moderadas y no moderadas para los contenidos.
            - Genera varios contenidos de prueba en distintos estados (borrador, inactivo, expirado).
        """
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
        """
        Restaura las señales y limpia los datos después de cada prueba.

        Propósito:
            Garantizar que las señales desconectadas en :meth:`setUp` sean reconectadas correctamente,
            evitando efectos secundarios en otros tests.

        Lógica:
            - Reconecta todas las señales relacionadas con los modelos `CustomUser` y `Category`.
            - Llama a :meth:`tearDown` de la clase base para realizar limpieza adicional.
        """

        pre_save.connect(cache_previous_user, sender=CustomUser)
        post_save.connect(post_save_user_handler, sender=CustomUser)
        pre_save.connect(cache_previous_category, sender=Category)
        post_save.connect(post_save_category_handler, sender=Category)
        pre_delete.connect(cache_category_before_delete, sender=Category)
        post_delete.connect(handle_category_after_delete, sender=Category)
        super().tearDown()

    # Pruebas para la vista kanban_board
    def test_user_without_permissions(self):
        """
        Verifica que un usuario sin permisos no pueda acceder al tablero Kanban.

        Lógica:
            - Inicia sesión con un usuario sin permisos específicos.
            - Realiza una solicitud GET al tablero Kanban.
            - Verifica que el estado de respuesta sea 403 (prohibido).
        """
        # Iniciar sesión con un usuario sin permisos
        self.client.login(email='user@mail.com', password='testpassword')

        # Realizamos una solicitud al tablero Kanban
        response = self.client.get(reverse('kanban_board'))

        # Verificar si el usuario es redirigido a la página de login
        self.assertEqual(response.status_code, 403,
                         "El usuario sin permisos no debería poder acceder al tablero Kanban.")

    def test_user_with_create_content_permission(self):
        """
        Verifica que un usuario con permiso de creación pueda acceder al tablero Kanban.

        Lógica:
            - Otorga al usuario el permiso para crear contenido.
            - Inicia sesión con el usuario y realiza una solicitud GET al tablero Kanban.
            - Verifica que el estado de respuesta sea 200 (éxito).
            - Confirma que el contenido en estado "Borrador" esté presente en la respuesta.
        """
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
        """
        Verifica que un usuario con permiso de edición pueda acceder al tablero Kanban.

        Lógica:
            - Otorga al usuario el permiso para editar contenido.
            - Inicia sesión y realiza una solicitud GET al tablero Kanban.
            - Verifica que el estado de respuesta sea 200.
            - Confirma que el contenido en estado "Edición" esté presente en la respuesta.
        """
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
        """
        Verifica que un usuario con permiso de publicación pueda acceder al tablero Kanban.

        Lógica:
            - Otorga al usuario el permiso para publicar contenido.
            - Inicia sesión y realiza una solicitud GET al tablero Kanban.
            - Verifica que el estado de respuesta sea 200.
            - Confirma que el contenido en estado "Publicado" esté presente en la respuesta.
        """
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
        """
        Verifica que un usuario con permiso para editar el estado activo pueda acceder al tablero Kanban.

        Lógica:
            - Otorga al usuario el permiso `edit_is_active`.
            - Inicia sesión y realiza una solicitud GET al tablero Kanban.
            - Verifica que el estado de respuesta sea 200.
            - Confirma que el contenido en estado "Publicado" esté presente en la respuesta.
        """
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
        """
        Verifica que la API `update_content_state` no permita el método GET.

        Lógica:
            - Crea un contenido de prueba.
            - Realiza una solicitud GET a la API `update_content_state` con el ID del contenido.
            - Verifica que el estado de respuesta sea 405 (método no permitido).
            - Verifica que el mensaje de error corresponda al método no permitido.
        """
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
        """
        Verifica que un creador pueda mover su contenido de borrador a revisión.

        Lógica:
            - Inicia sesión con el creador del contenido.
            - Envía una solicitud POST a la API `update_content_state` para cambiar el estado a "revisión".
            - Confirma que el estado del contenido ha cambiado a "revisión".
        """
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
        """
        Verifica que un creador pueda mover su contenido a publicado en una categoría no moderada.

        Lógica:
            - Inicia sesión con el creador.
            - Envía una solicitud POST para cambiar el estado a "publicado".
            - Confirma que el estado del contenido ha cambiado a "publicado".
        """
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
        """
        Verifica que un creador pueda mover su propio contenido de publicado a inactivo.

        Lógica:
            - Cambia el contenido a "publicado".
            - Inicia sesión con el creador y envía una solicitud POST para cambiar el estado a "inactivo".
            - Confirma que el estado del contenido ha cambiado a "inactivo".
        """
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
        """
        Verifica que un creador no pueda cambiar el estado de contenido que no le pertenece.

        Lógica:
            - Inicia sesión con el creador.
            - Intenta mover el contenido de otro usuario a "revisión".
            - Confirma que el estado del contenido no ha cambiado.
        """
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
        """
        Verifica que un editor pueda mover contenido de revisión a "a publicar".

        Lógica:
            - Cambia el contenido a "revisión".
            - Inicia sesión con el editor y envía una solicitud POST para mover el contenido a "a publicar".
            - Confirma que el estado del contenido ha cambiado a "a publicar".
        """
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
        """
        Verifica que un editor pueda mover contenido de revisión a borrador.

        Lógica:
            - Cambia el contenido a "revisión".
            - Inicia sesión con el editor y envía una solicitud POST para mover el contenido a "borrador".
            - Confirma que el estado del contenido ha cambiado a "borrador".
        """
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
        """
        Verifica que un publicador pueda mover contenido de "a publicar" a publicado.

        Lógica:
            - Cambia el contenido a "a publicar".
            - Inicia sesión con el publicador y envía una solicitud POST para mover el contenido a "publicado".
            - Confirma que el estado del contenido ha cambiado a "publicado".
        """
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
        """
        Verifica que un publicador pueda mover contenido de "a publicar" a revisión.

        Lógica:
            - Cambia el contenido a "a publicar".
            - Inicia sesión con el publicador y envía una solicitud POST para mover el contenido a "revisión".
            - Confirma que el estado del contenido ha cambiado a "revisión".
        """
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
        """
        Verifica que un usuario con el permiso `edit_is_active` pueda mover contenido de publicado a inactivo.

        Lógica:
            - Cambia el contenido a "publicado".
            - Inicia sesión con el usuario con permiso `edit_is_active` y envía una solicitud POST para mover el contenido a "inactivo".
            - Confirma que el estado del contenido ha cambiado a "inactivo".
        """
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
        """
        Verifica que un creador pueda mover contenido inactivo a publicado si no ha expirado.

        Lógica:
            - Inicia sesión con el creador.
            - Envía una solicitud POST para mover el contenido de inactivo a "publicado".
            - Confirma que el estado del contenido ha cambiado a "publicado".
        """
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
        """
        Verifica que un creador no pueda mover contenido expirado de inactivo a publicado.

        Lógica:
            - Inicia sesión con el creador.
            - Intenta mover un contenido expirado a "publicado".
            - Confirma que el contenido sigue en estado "inactivo" y no ha sido publicado.
        """
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


class ReportModelTest(TestCase):
    """
    Pruebas unitarias para el modelo `Report`, que asegura que los reportes se puedan crear y manejen adecuadamente
    los atributos y relaciones definidas en el modelo.

    :methods:
        - setUp: Configura el entorno de prueba creando un usuario, una categoría y un contenido de prueba.
        - tearDown: Restaura las señales desconectadas para asegurar que las pruebas no interfieran con el funcionamiento normal.
        - test_create_report: Verifica la creación correcta de un reporte asociado con un contenido, comprobando que los atributos del reporte coincidan con los valores esperados.
    """

    def setUp(self):
        """
        Configura el entorno necesario para las pruebas.

        :actions:
            - Desconecta la señal `post_save` de `Category` para evitar efectos colaterales.
            - Crea un usuario, una categoría y un contenido de prueba.
        """
        # Desconectar la señal post_save para Category
        post_save.disconnect(post_save_category_handler, sender=Category)
        
        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='reportuser@example.com',
            name='Report User',
            password='password123'
        )
        
        # Crear una categoría de prueba
        self.category = Category.objects.create(
            name='Test Category',
            description='Descripción de prueba'  # Proporcionar una descripción si es necesario
        )
        
        # Crear un contenido de prueba con autor y categoría
        self.content = Content.objects.create(
            title='Test Content',
            summary='Summary for test content',
            autor=self.user,
            category=self.category,
            state='draft',
            date_create=timezone.now(),
        )

    def tearDown(self):
        """
        Restaura las señales desconectadas al finalizar las pruebas.

        :actions:
            - Reconecta la señal `post_save` para `Category` para restablecer su comportamiento normal.
        """
        # Reconectar la señal después de la prueba
        post_save.connect(post_save_category_handler, sender=Category)

    def test_create_report(self):
        """
        Verifica la creación correcta de un reporte asociado con un contenido.

        :actions:
            - Crea una instancia del modelo `Report` asociada con un contenido de prueba.
            - Comprueba que los atributos del reporte coincidan con los valores esperados.

        :assertions:
            - Verifica que `content` coincida con el contenido de prueba.
            - Verifica que `reported_by` coincida con el usuario de prueba.
            - Verifica que `email`, `name`, `reason` y `description` contengan los valores definidos.
        """
        report = Report.objects.create(
            content=self.content,
            reported_by=self.user,
            email='user@example.com',
            name='Test Reporter',
            reason='spam',
            description='Este es un reporte de prueba.',
            created_at=timezone.now()
        )
        self.assertEqual(report.content, self.content)
        self.assertEqual(report.reported_by, self.user)
        self.assertEqual(report.email, 'user@example.com')
        self.assertEqual(report.name, 'Test Reporter')
        self.assertEqual(report.reason, 'spam')
        self.assertIn('reporte de prueba', report.description)



class ReportFormTest(TestCase):
    """
    Pruebas unitarias para el formulario `ReportForm`, asegurando que se manejen correctamente los datos iniciales,
    los datos válidos e inválidos al crear un reporte.

    :methods:
        - setUp: Configura el entorno de prueba creando un usuario de prueba para usar en los formularios.
        - test_form_initial_data_for_authenticated_user: Verifica que los campos `name` y `email` se inicialicen correctamente con los datos del usuario autenticado.
        - test_form_invalid_data: Verifica que el formulario sea inválido cuando los datos proporcionados no son correctos.
        - test_form_valid_data: Verifica que el formulario sea válido cuando se proporcionan datos correctos para crear un reporte.
    """
    def setUp(self):
        """
        Configura el entorno de prueba creando un usuario.

        :actions:
            - Crea un usuario con email, nombre y contraseña para usar en las pruebas del formulario.
        """
        self.user = get_user_model().objects.create_user(
            email='formuser@example.com',
            name='Form User',
            password='password123'
        )

    def test_form_initial_data_for_authenticated_user(self):
        """
        Verifica que los campos `name` y `email` se inicialicen correctamente con los datos del usuario autenticado.

        :actions:
            - Inicializa el formulario `ReportForm` con un usuario autenticado.
            - Comprueba que los campos `name` y `email` del formulario contengan los valores esperados.
        """

        form = ReportForm(user=self.user)
        self.assertEqual(form.fields['name'].initial, 'Form User')
        self.assertEqual(form.fields['email'].initial, 'formuser@example.com')

    def test_form_invalid_data(self):
        """
        Verifica que el formulario sea inválido cuando los datos proporcionados no son correctos.

        :actions:
            - Proporciona datos inválidos (por ejemplo, un email con formato incorrecto).
            - Verifica que el formulario no sea válido.
            - Comprueba que los errores incluyan los campos esperados (`name` y `email`).
        """

        form_data = {'name': '', 'email': 'invalidemail', 'reason': 'spam', 'description': 'Test description'}
        form = ReportForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)
    
    def test_form_valid_data(self):
        """
        Verifica que el formulario sea válido cuando se proporcionan datos correctos para crear un reporte.

        :actions:
            - Proporciona datos válidos para el formulario.
            - Verifica que el formulario sea válido.
        """

        form_data = {'name': 'Test User', 'email': 'testuser@example.com', 'reason': 'spam', 'description': 'Valid report'}
        form = ReportForm(data=form_data)
        self.assertTrue(form.is_valid())

class ReportPostViewTest(TestCase):
    """
    Pruebas unitarias para la vista `report_post`, que maneja la creación de reportes asociados a contenidos.

    :methods:
        - setUp: Configura el entorno de prueba creando un usuario, categoría y contenido de prueba.
        - tearDown: Reconecta la señal `post_save` para `Category` después de cada prueba.
        - test_post_valid_report: Verifica que se pueda crear un reporte correctamente con datos válidos.
        - test_post_invalid_report: Verifica el manejo de datos inválidos, asegurando que el formulario no se acepte.
        - test_post_report_ajax: Verifica el comportamiento de la vista al realizar una solicitud AJAX, asegurando una respuesta adecuada.
    """

    def setUp(self):
        """
        Configura el entorno de prueba creando un usuario, categoría y contenido de prueba.

        :actions:
            - Desconecta la señal `post_save` para `Category` para evitar efectos secundarios.
            - Crea un usuario de prueba, una categoría y un contenido asociado a dicha categoría.
            - Establece la URL de la vista de reportes y autentica al usuario de prueba.
        """

        # Desconectar la señal post_save para Category
        post_save.disconnect(post_save_category_handler, sender=Category)

        # Crear un usuario de prueba
        self.user = get_user_model().objects.create_user(
            email='viewuser@example.com',
            name='View User',
            password='password123'
        )

        # Crear una categoría de prueba
        self.category = Category.objects.create(
            name='Test Category',
            description='Descripción de prueba'  # Asegura que la descripción sea compatible si es requerida
        )

        # Crear un contenido de prueba con autor y categoría
        self.content = Content.objects.create(
            title='Content for reporting',
            summary='Summary for test content',
            autor=self.user,
            category=self.category,  # Se asigna la categoría para evitar problemas de relación
            state='draft',
            date_create=timezone.now()
        )

        # URL para la vista de reportes
        self.url = reverse('report_post', args=[self.content.id])

        # Autenticarse como el usuario de prueba
        self.client.login(email='viewuser@example.com', password='password123')

    def tearDown(self):
        """
        Reconecta la señal `post_save` para `Category` después de cada prueba.

        :actions:
            - Reconecta la señal `post_save` para garantizar que el entorno vuelva a su estado normal tras cada prueba.
        """

        post_save.connect(post_save_category_handler, sender=Category)

    def test_post_valid_report(self):
        """
        Verifica que se pueda crear un reporte correctamente con datos válidos.

        :actions:
            - Envía una solicitud POST con datos válidos para crear un reporte.
            - Verifica que la respuesta sea una redirección exitosa (código 302).
            - Comprueba que el reporte se haya creado correctamente en la base de datos.
        """

        response = self.client.post(self.url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'reason': 'spam',
            'description': 'Testing report'
        })

        # Verificar que se redirige correctamente y se crea el reporte
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Report.objects.filter(content=self.content).exists())

    def test_post_invalid_report(self):
        """
        Verifica el manejo de datos inválidos, asegurando que el formulario no se acepte.

        :actions:
            - Envía una solicitud POST con datos inválidos (por ejemplo, email incorrecto o campos vacíos).
            - Verifica que la respuesta sea un error (código 400).
            - Comprueba que se muestre el mensaje de error esperado en la respuesta.
        """
        response = self.client.post(self.url, {
            'name': '',
            'email': 'invalidemail',
            'reason': 'spam',
            'description': ''
        })

        # Verificar que se recibe un código de error y el mensaje esperado
        self.assertEqual(response.status_code, 400)
        self.assertIn('No se permite acceso directo', response.content.decode())

    def test_post_report_ajax(self):
        """
        Verifica el comportamiento de la vista al realizar una solicitud AJAX, asegurando una respuesta adecuada.

        :actions:
            - Envía una solicitud POST usando AJAX para crear un reporte.
            - Verifica que la respuesta sea un éxito (código 200) y contenga datos JSON indicando éxito.
            - Comprueba que el reporte se haya creado correctamente en la base de datos.
        """

        response = self.client.post(self.url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'reason': 'spam',
            'description': 'Testing report'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Verificar que se recibe una respuesta JSON de éxito
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('success'), True)
        self.assertTrue(Report.objects.filter(content=self.content).exists())
