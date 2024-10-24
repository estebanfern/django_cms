from django.template.response import TemplateResponse
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rating.models import Rating
from notification.tasks import notify_new_content_suscription
from . import service
from .forms import ReportForm
from django.contrib.admin import site as admin_site
import notification.service
from category.models import Category
from .models import Content, Report
import json
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import ContentForm
from django.core.exceptions import PermissionDenied
from simple_history.utils import update_change_reason
from django.contrib import messages
from django.urls import reverse
from .service import validate_permission_kanban
from .tasks import update_reactions, count_view, count_share

@login_required
def kanban_board(request):
    """
    Muestra el tablero Kanban con los contenidos filtrados según los permisos del usuario.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest

    :return: Renderiza la vista 'kanban_board.html' con los contenidos y permisos correspondientes.
    :rtype: HttpResponse
    """
    user = request.user

    if not (
        user.has_perm('app.create_content') or 
        user.has_perm('app.edit_content') or 
        user.has_perm('app.publish_content') or
        user.has_perm('app.edit_is_active')
    ):
        raise PermissionDenied
    
    contents = {
        'Borrador': [],
        'Edicion': [],
        'A publicar': [],
        'Publicado': [],
        'Inactivo': [],
    }

    # Filtrar contenidos según los permisos del usuario y que estén activos
    if user.has_perm('app.edit_content') or user.has_perm('app.publish_content') or user.has_perm('app.edit_is_active'):
        # Los editores y publicadores ven todos los contenidos activos sin importar el autor
        contents['Borrador'] = Content.objects.filter(state='draft', is_active=True, category__is_active=True)
        contents['Edicion'] = Content.objects.filter(state='revision', is_active=True, category__is_active=True)
        contents['A publicar'] = Content.objects.filter(state='to_publish', is_active=True, category__is_active=True)
        contents['Publicado'] = Content.objects.filter(state='publish', is_active=True, category__is_active=True)
        contents['Inactivo'] = Content.objects.filter(state='inactive', is_active=True, category__is_active=True)
    elif user.has_perm('app.create_content'):
        # Los autores ven solo sus contenidos activos en cualquier estado
        contents['Borrador'] = Content.objects.filter(state='draft', autor=user, is_active=True, category__is_active=True)
        contents['Edicion'] = Content.objects.filter(state='revision', autor=user, is_active=True, category__is_active=True)
        contents['A publicar'] = Content.objects.filter(state='to_publish', autor=user, is_active=True, category__is_active=True)
        contents['Publicado'] = Content.objects.filter(state='publish', autor=user, is_active=True, category__is_active=True)
        contents['Inactivo'] = Content.objects.filter(state='inactive', autor=user, is_active=True, category__is_active=True)

    # Pasar permisos al contexto de la plantilla
    context = {
        'contents': contents,
        'can_create_content': user.has_perm('app.create_content'),
        'can_edit_content': user.has_perm('app.edit_content'),
        'can_publish_content': user.has_perm('app.publish_content'),
        'can_edit_is_active': user.has_perm('app.edit_is_active'),
    }
    return render(request, 'kanban/kanban_board.html', context)

@csrf_exempt
@login_required
def update_content_state(request, content_id):
    """
    API para actualizar el estado de un contenido específico basado en los permisos del usuario.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :param content_id: El ID del contenido cuyo estado se actualizará.
    :type content_id: int

    :return: Respuesta con el estado de la operación (éxito o error) y un mensaje informativo.
    :rtype: JsonResponse
    """

    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

    mappState = {
        'draft': 'Borrador',
        'revision': 'Edicion',
        'to_publish': 'A publicar',
        'publish': 'Publicado',
        'inactive': 'Inactivo',
    }

    user = request.user

    if not (
        user.has_perm('app.create_content') or
        user.has_perm('app.edit_content') or
        user.has_perm('app.publish_content') or
        user.has_perm('app.edit_is_active')
    ):
        raise PermissionDenied

    content = get_object_or_404(Content, id=content_id)
    if not content.is_active or not content.category.is_active:
        raise Http404
    oldState = content.state
    data = json.loads(request.body)
    new_state = data.get('state')
    reason = data.get('reason')

    # **Verificación: Evitar actualización si no hay cambio en el estado**
    if content.state == new_state:
        # No realizar la actualización ni registrar en el historial si el estado no cambia
        return JsonResponse({'status': 'no_change', 'message': 'El estado no ha cambiado, no se actualizará.'})

    # Verificar si el usuario tiene permisos para cambiar el estado
    response = service.validate_permission_kanban(user, content, new_state, oldState)
    if response['status'] == 'error':
        return JsonResponse(response, status=403)

    # Verificar si el contenido está expirado
    if new_state == 'publish' and oldState == 'inactive' and timezone.now() >= content.date_expire:
        return JsonResponse({'status': 'error', 'message': 'No se puede publicar un contenido expirado.'}, status=403)

    # Verificar si el  contenido no tiene fecha de publicacion o si la fecha de publicacion es menor a la actual
    if new_state == 'publish' and oldState != 'inactive' and (content.date_published is None or content.date_published < timezone.now()):
        content.date_published = timezone.now()

    if not reason:
        reason = f"Cambio de estado de {mappState[oldState]} a {mappState[new_state]}"

    content.state = new_state
    content.save()
    update_change_reason(content, reason)

    if new_state == 'publish':
        if content.date_published <= timezone.now():
            notify_new_content_suscription.delay(content_id) # Notificar a los suscriptores inmediatamente
        else:
            notify_new_content_suscription.apply_async((content_id,), eta=content.date_published) # Programar la notificación para la fecha de publicación

    notification.service.changeState([content.autor.email], content, oldState)
    return JsonResponse({'status': 'success'})

@csrf_exempt
@login_required
def validate_permission_kanban_api(request):
    """
    API para validar los permisos de cambio de estado en el tablero Kanban.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest

    :return: JsonResponse con el resultado de la validación.
    :rtype: JsonResponse
    """
    if not request.method == 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

    # Obtener los datos de la petición
    user = request.user
    data = json.loads(request.body)
    content_id = data.get('content_id', None)
    new_state = data.get('new_state', None)
    old_state = data.get('old_state', None)

    # Validar que los datos sean correctos
    if not user or not content_id or not new_state or not old_state:
        return JsonResponse({'status': 'error', 'message': 'Datos incorrectos.'}, status=400)

    # Obtener el contenido
    content = get_object_or_404(Content, id=content_id)

    # Validar los permisos
    validation_result = validate_permission_kanban(user=user, content=content, newState=new_state, oldState=old_state)

    # validation_result en un JsonResponse
    if validation_result['status'] == 'error':
        return JsonResponse(validation_result, status=403)
    return JsonResponse(validation_result, status=200)


class ContentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Vista para la creación de contenido.

    Hereda de:
        - LoginRequiredMixin: Requiere que el usuario esté autenticado.
        - PermissionRequiredMixin: Requiere permisos específicos para acceder a la vista.
        - CreateView: Proporciona la funcionalidad para crear objetos.

    Atributos:
        model (Content): Modelo del contenido a crear.
        form_class (ContentForm): Formulario asociado para la creación de contenido.
        template_name (str): Nombre de la plantilla para la vista de creación.
        success_url (str): URL a redirigir tras la creación exitosa del contenido.
        permission_required (str): Permiso requerido para acceder a la vista.
    """

    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = '/tablero/' # a donde ir despues
    permission_required = 'app.create_content'

    def get_form(self, form_class=None):
        """
        Obtiene el formulario para la creación de contenido.

        :param form_class: Clase del formulario a obtener. Si no se proporciona, se utilizará la clase de formulario predeterminada.
        :type form_class: class, opcional
        :return: El formulario modificado, eliminando el campo 'change_reason' para que no se muestre.
        :rtype: Form
        """

        form = super().get_form(form_class)
        # Elimina el campo 'change_reason' para que no se muestre en el formulario de creación
        del form.fields['change_reason']
        return form

    def form_valid(self, form):
        """
        Valida el formulario y guarda el contenido si es válido.

        Lógica:
            - Verifica que la fecha de publicación no sea posterior a la fecha de expiración.
            - Guarda el contenido y sus relaciones M2M (tags).
            - Establece la razón de cambio en el historial como 'Creación de contenido'.
            - Redirige a la URL de éxito tras la creación exitosa del contenido.

        :param form: Formulario con los datos del contenido.
        :type form: ContentForm
        :return: Redirige a la URL de éxito si la validación es correcta.
        :rtype: HttpResponseRedirect
        """

        # La fecha de publicacion no debe ser igual a la de expiracion
        date_published = form.cleaned_data.get('date_published')
        date_expire = form.cleaned_data.get('date_expire')

        if date_published and date_expire and date_published.date() > date_expire.date():
            messages.warning(self.request, 'La fecha de publicación debería ser antes de la fecha de expiración del contenido')
            return self.form_invalid(form)

        content = form.save(commit=False)
        content.autor = self.request.user
        content.is_active = True
        content.date_create = timezone.now()
        content.state = Content.StateChoices.draft
        content.save()

        # Guarda las relaciones M2M (tags)
        form.save_m2m()

        # Establece la razón de cambio en el historial como 'Creación de contenido'
        update_change_reason(content, 'Creación de contenido')

        messages.success(self.request, 'Contenido creado exitosamente')
        return redirect(self.success_url)
        
    def form_invalid(self, form):
        """
        Maneja el caso en que el formulario no sea válido.

        :param form: Formulario con los datos incorrectos.
        :type form: ContentForm
        :return: Renderiza la respuesta con el formulario inválido.
        :rtype: HttpResponse
        """

        return self.render_to_response(self.get_context_data(form=form))


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para la actualización de contenido.

    Hereda de:
        - LoginRequiredMixin: Requiere que el usuario esté autenticado.
        - UpdateView: Proporciona la funcionalidad para actualizar objetos.

    Atributos:
        model (Content): Modelo del contenido a actualizar.
        form_class (ContentForm): Formulario asociado para la actualización de contenido.
        template_name (str): Nombre de la plantilla para la vista de actualización.
        success_url (str): URL a redirigir tras la actualización exitosa del contenido.
    """

    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = '/tablero/'

    # Lista de permisos
    required_permissions = ['app.create_content', 'app.edit_content']

    def dispatch(self, request, *args, **kwargs):
        """
        Verifica los permisos del usuario antes de permitir la actualizacion del contenido.

        Acciones:
            - Verifica si el usuario tiene al menos uno de los permisos requeridos para acceder a la vista.
            - Permite la edición solo si:
                - El usuario tiene permisos de edición y el contenido está en estado de revisión, o
                - El usuario es el autor del contenido, tiene permisos de creación, y el contenido está en borrador.
            - Si no cumple con los requisitos, se levanta un error de 'PermissionDenied'.

        Parametros:
            request (HttpRequest): El objeto de la solicitud HTTP.
            args: Argumentos adicionales.
            kwargs: Argumentos adicionales de palabras clave.

        Retorna:
            HttpResponse: La respuesta de la vista si se cumplen los permisos.
        """

        # Verifica si el usuario tiene al menos uno de los permisos requeridos
        if not any(request.user.has_perm(perm) for perm in self.required_permissions):
            raise PermissionDenied

        if not self.get_object().is_active or not self.get_object().category.is_active:
            raise Http404

        # Verifica que solo el autor del contenido edite su contenido en borrador
        # o que si sos editor el cotenido este en revision para poder editar/
        if self.request.user.has_perm('app.edit_content') and self.get_object().state == Content.StateChoices.revision:
            # Tiene permisos de edición, siga
            pass
        elif self.request.user.id == self.get_object().autor_id and self.request.user.has_perm('app.create_content') and self.get_object().state == Content.StateChoices.draft:
            # Es tu contenido, sos autor y tu contenido está en borrador, pase
            pass
        else:
            # No cumplis con alguno de los requisitos, F
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


    def get_initial(self):
        """
        Obtiene los datos iniciales para el formulario, considerando posibles datos históricos.

        Acciones:
            - Recupera el `history_id` desde los parámetros de la URL.
            - Si `history_id` está presente, carga los datos históricos del contenido correspondiente.
            - Retorna los datos iniciales históricos para el formulario.

        Retorna:
            dict: Diccionario con los datos iniciales para el formulario.
        """

        # Recuperar el history_id desde los parámetros de la URL
        history_id = self.request.GET.get('history_id')

        # Si history_id está presente, cargar los datos históricos
        if history_id:
            historical_record = get_object_or_404(Content.history.model, history_id=history_id)
            initial_data = {
                'title': historical_record.title,
                'summary': historical_record.summary,
                'category': historical_record.category,
                'date_expire': historical_record.date_expire,
                'date_published': historical_record.date_published,
                'content': historical_record.content,
            }
            return initial_data
        return super().get_initial()


    def get_form(self, form_class=None):
        """
        Obtiene el formulario para la actualización del contenido.

        Parámetros:
            form_class (Class, opcional): Clase del formulario a obtener. Si no se proporciona, se utiliza la clase de formulario predeterminada.

        Acciones:
            - Llama al método 'get_form' del padre para obtener el formulario inicial.
            - Si el contenido está en estado de borrador, elimina el campo 'change_reason' del formulario.

        Retorna:
            Form: El formulario modificado, si es necesario, sin el campo 'change_reason'.
        """

        form = super().get_form(form_class)
        if self.get_object().state == Content.StateChoices.draft:
            del form.fields['change_reason']
        return form
    
    def form_valid(self, form):
        """
        Valida el formulario y actualiza el contenido, registrando la razón de los cambios.

        Parámetros:
            form (Form): Formulario con los datos del contenido a actualizar.

        Acciones:
            - Verifica si la fecha de publicación no es posterior a la fecha de expiración.
            - Si el usuario es el autor y el contenido está en borrador, actualiza todos los campos del formulario.
            - Si el usuario es un editor y el contenido está en revisión, solo se permite actualizar el campo 'content'.
            - Guarda el contenido y registra la razón del cambio si se proporciona.

        Retorna:
            HttpResponseRedirect: Redirige a la URL de éxito definida si el formulario es válido.
        """
        user = self.request.user

        # Recupera el objeto original desde la base de datos
        content = self.get_object()

        change_reason = None

        if user.id == content.autor_id and user.has_perm('app.create_content') and content.state == Content.StateChoices.draft:
        # Si el usuario es el autor del contenido. tiene permisos de autoria y el cotenido está en estado borrador, OK

            #La fecha de publicacion no debe ser igual a la de expiracion
            date_published = form.cleaned_data.get('date_published')
            date_expire = form.cleaned_data.get('date_expire')

            if date_published and date_expire and date_published.date() > date_expire.date():
                messages.warning(self.request, 'La fecha de publicación debería ser antes de la fecha de expiración del contenido')
                return self.form_invalid(form)


            form_data = form.cleaned_data
            for field in form_data:
                setattr(content, field, form_data[field])

            change_reason = 'Modificaciones de autor'

            content = form.save(commit=False)
            tags = form.cleaned_data.get('tags', None)
            if tags:
                content.tags.set(tags)
        elif user.has_perm('app.edit_content') and content.state == Content.StateChoices.revision:
        # Si el usuario es un editor y el contenido está en revision
            content.content = form.cleaned_data['content']
            change_reason = form.cleaned_data.get('change_reason', '')
        else:
            raise PermissionDenied

        content.save()


        if change_reason:
            update_change_reason(content, change_reason)

        messages.success(self.request, 'Contenido modificado exitosamente.')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        """
        Maneja la respuesta si el formulario es inválido.

        Parámetros:
            form (Form): Formulario con los datos inválidos.

        Acciones:
            - Llama al método 'form_invalid' del padre para manejar la respuesta cuando el formulario no es válido.

        Retorna:
            HttpResponse: Respuesta con el formulario y los errores correspondientes.
        """
        return super().form_invalid(form)


def view_content(request, id):
    """
    Vista para mostrar el contenido detallado.

    :param request: El objeto de la solicitud HTTP.
    :type request: HttpRequest
    :param id: ID del contenido a visualizar.
    :type id: int

    :return: Renderiza la plantilla 'content/view.html' con el contenido y su historial.
    :rtype: HttpResponse
    """
    content = get_object_or_404(Content, id=id)
    if not content.is_active or not content.category.is_active:
        raise Http404

    user = request.user
    # Verificar que si el usuario esta registrado y esta queriendo ver un contenido de categoria de suscripcion o pago
    # en caso de que no, redirigirle al login con un mensaje
    # TODO: verificar que el usuario este suscripto y al dia si es un contenido de categoria de pago
    if not user.is_authenticated and not content.category.type == Category.TypeChoices.public:
        messages.warning(request, 'Para poder acceder a contenidos de categorias de suscripción o pago debes estar registrado')
        return redirect('login')

    if (not content.state == Content.StateChoices.publish) or (content.date_published and content.date_published > timezone.now()):
        if not (user.has_perm('app.create_content') or user.has_perm('app.edit_content') or user.has_perm('app.publish_content') or user.has_perm('app.edit_is_active')):
            raise Http404

    history = content.history.all().order_by('-history_date')
    # Obtener si el usuario ha dado like o dislike
    reaction_status = 'none'
    user_has_liked = content.likes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    user_has_disliked = content.dislikes.filter(id=request.user.id).exists() if request.user.is_authenticated else False
    if user_has_liked: reaction_status = 'liked'
    elif user_has_disliked: reaction_status = 'disliked'

    # Verificar si el usuario ya ha dado una calificación (rating) al contenido
    user_rating = 0
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, content=content).rating
        except Rating.DoesNotExist:
            user_rating = 0  # Si no ha dado ninguna calificación, usar 0

    # Aumentar la cantidad de vistas del contenido
    count_view.delay(content.id)

    # Pasar todos los datos necesarios al contexto
    return render(request, 'content/view.html', {
        "content": content,
        "history": history,
        "reaction_status": reaction_status,
        "user_rating": user_rating,
        "is_authenticated": request.user.is_authenticated,  # Para verificar en el frontend
    })

@login_required
def view_version(request, content_id, history_id):
    """
    Vista para mostrar una versión específica de un contenido basado en su historial.

    :param request: El objeto de la solicitud HTTP.
    :type request: HttpRequest
    :param content_id: ID del contenido.
    :type content_id: int
    :param history_id: ID del historial para la versión a visualizar.
    :type history_id: int

    :return: Renderiza la plantilla 'content/view_version.html' con el contenido y la versión del historial.
    :rtype: HttpResponse
    """
    user = request.user
    content = get_object_or_404(Content, id=content_id)

    if user.has_perm('app.create_content') and user.id == content.autor_id:
        pass
    elif (user.has_perm('app.edit_content') 
          or user.has_perm('app.publish_content')
          or user.has_perm('app.edit_is_active')
            ):
        pass
    else:
        raise PermissionDenied

    history = content.history.filter(history_id=history_id).first()

    if not history or not content.is_active:
        raise Http404
    return render(request, 'content/view_version.html', {"content" : content, "history" : history})


def report_post(request, content_id):
    """
    Maneja la lógica para reportar un contenido.

    :param request: La solicitud HTTP realizada por el usuario.
    :type request: HttpRequest
    :param content_id: El ID del contenido que se va a reportar.
    :type content_id: int

    :return: Una respuesta HTTP, que puede ser un JSON, una redirección, o un error 400.
    :rtype: HttpResponse
    """

    post = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user)
        if form.is_valid():
            report = form.save(commit=False)
            report.content = post
            if request.user.is_authenticated:
                report.reported_by = request.user
            report.save()

        
            messages.success(request, 'Contenido reportado exitosamente.')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return HttpResponseRedirect(reverse('content_view', args=[post.id]))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                return HttpResponseBadRequest("No se permite acceso directo")
    else:
        form = ReportForm(user=request.user)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'content/report_form_partial.html', {'form': form, 'post': post})
        else:
            return HttpResponseBadRequest("No se permite acceso directo")

def like_content(request, content_id):
    """
    Gestiona la acción de 'me gusta' en un contenido por parte del usuario.

    :param request: La solicitud HTTP realizada por el usuario.
    :type request: HttpRequest
    :param content_id: El ID del contenido que se va a marcar con 'me gusta'.
    :type content_id: int

    :return: Respuesta en JSON con el estado de la operación.
    :rtype: JsonResponse
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Para poder reaccionar a contenidos debes estar registrado'}, status=403)

    content = get_object_or_404(Content, id=content_id)

    if content.likes.filter(id=request.user.id).exists():
        content.likes.remove(request.user)
        message = "Me gusta eliminado"
        result = "deleted"
    else:
        content.likes.add(request.user)
        content.dislikes.remove(request.user)
        message = "Me gusta agregado"
        result = "created"

    update_reactions.delay(content.id)
    return JsonResponse({
        'status': 'success',
        'message': message,
        'result': result,
    })

def dislike_content(request, content_id):
    """
    Gestiona la acción de 'no me gusta' en un contenido por parte del usuario.

    :param request: La solicitud HTTP realizada por el usuario.
    :type request: HttpRequest
    :param content_id: El ID del contenido que se va a marcar con 'no me gusta'.
    :type content_id: int

    :return: Respuesta en JSON con el estado de la operación.
    :rtype: JsonResponse
    """

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Para poder reaccionar a contenidos debes estar registrado'}, status=403)

    content = get_object_or_404(Content, id=content_id)

    if content.dislikes.filter(id=request.user.id).exists():
        content.dislikes.remove(request.user)
        message = "No me gusta eliminado"
        result = "deleted"
    else:
        content.dislikes.add(request.user)
        content.likes.remove(request.user)
        message = "No me gusta agregado"
        result = "created"

    update_reactions.delay(content.id)
    return JsonResponse({
        'status': 'success',
        'message': message,
        'result': result,
    })

def report_detail(request, report_id):
    """
    Muestra los detalles de un reporte en una vista personalizada.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        report_id (int): ID del reporte cuyos detalles se van a visualizar.

    Comportamiento:
        - Obtiene el reporte utilizando el ID proporcionado o devuelve un error 404 si no existe.
        - Obtiene las opciones de metadatos del modelo `Report` para usarlas en la plantilla.
        - Renderiza la plantilla `report_detail.html` con el reporte y sus metadatos.

    Retorna:
        HttpResponse: La respuesta renderizada con los detalles del reporte.
    """
    user = request.user
    if not (
        user.has_perm('app.view_reports')
    ):
        raise PermissionDenied

    report = get_object_or_404(Report, pk=report_id)
    content = report.content
    opts = content._meta
    context = dict(
        admin_site.each_context(request),  # Contexto del admin
        report=report,
        content=content,
        opts=opts,
    )
    return TemplateResponse(request, 'admin/content/report/report_detail.html', context)

def view_content_detail(request, content_id):
    """
    Muestra los detalles de un contenido en una vista personalizada.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        content_id (int): ID del contenido cuyos detalles se van a visualizar.

    Comportamiento:
        - Obtiene el contenido utilizando el ID proporcionado o devuelve un error 404 si no existe.
        - Obtiene las opciones de metadatos del modelo `Content` para usarlas en la plantilla.
        - Renderiza la plantilla `content_detail.html` con el contenido y sus metadatos.

    Retorna:
        HttpResponse: La respuesta renderizada con los detalles del contenido.
    """
    user = request.user
    if not (
        user.has_perm('app.view_content')
    ):
        raise PermissionDenied

    content = get_object_or_404(Content, pk=content_id)
    opts = content._meta
    context = dict(
        admin_site.each_context(request),  # Contexto del admin
        content=content,
        opts=opts,
    )
    return TemplateResponse(request, 'admin/content/content/content_detail.html', context)

def view_count_share(request, content_id):
    """
    Encola en el worker de Celery la tarea para incrementar el contador de compartidos de un contenido.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP.
        contend_id (int): ID del contenido cuyo contador de compartidos se incrementará.

    Comportamiento:
        - Encola al worker de Celery la tarea `count_share` con el ID del contenido.

    Retorna:
        JsonResponse: Respuesta JSON con el estado de la operación.
    """
    count_share.delay(content_id)
    return JsonResponse({'status': 'success', 'message': 'Enqueued task.'})
