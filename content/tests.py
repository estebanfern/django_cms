from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from app.models import CustomUser
from category.models import Category
from content.forms import ContentForm
from content.models import Content

class ContentCreateViewTest(TestCase):
    def setUp(self):
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

    def test_access_create_content_with_permission(self):
        """
        Verifica que un usuario autenticado con permiso adecuado puede acceder a la vista de creación de contenido.
        """
        url = reverse('content-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Se esperaba un código de estado 200 para un usuario con permisos.")
        self.assertTemplateUsed(response, 'content/content_form.html', "Se esperaba usar la plantilla 'content/content_form.html'.")

    def test_access_create_content_without_permission(self):
        """
        Verifica que un usuario sin permiso para crear contenido recibe un error 403 al intentar acceder a la vista de creación.
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
    def setUp(self):
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

    def test_update_content_view(self):
        """
        Verifica que un usuario con permiso puede acceder a la vista de actualización de contenido.
        """
        url = reverse('content-update', args=[self.content.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, "Se esperaba un código de estado 200 para un usuario con permisos.")
        self.assertTemplateUsed(response, 'content/content_form.html', "Se esperaba usar la plantilla 'content/content_form.html'.")

    def test_form_valid_content_update(self):
        """
        Verifica que un usuario con permisos puede actualizar el contenido correctamente y es redirigido después de la actualización.
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
    def setUp(self):
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

    def test_update_content_view_for_editor(self):
        """
        Verifica que un editor puede acceder a la vista de actualización de contenido en estado revisión.
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

    def setUp(self):
        # Crear usuario y categoría de prueba
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            name='Test User',
            password='testpassword123'
        )
        self.category = Category.objects.create(name='Test Category')

    def test_content_form_creation_valid(self):
        """
        Verifica que el formulario de creación de contenido es válido con los datos correctos.
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
