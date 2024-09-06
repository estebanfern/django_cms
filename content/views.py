from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from .models import Content
import json
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .forms import ContentForm
from django.core.exceptions import PermissionDenied
from simple_history.utils import update_change_reason
from django.contrib import messages


@login_required
def kanban_board(request):
    user = request.user
    contents = {
        'Borrador': [],
        'Edicion': [],
        'A publicar': [],
        'Publicado': [],
        'Inactivo': [],
    }

    # Filtrar contenidos según los permisos del usuario y que estén activos
    if user.has_perm('app.create_content'):
        # Los autores ven solo sus contenidos activos en cualquier estado
        contents['Borrador'] = Content.objects.filter(state='draft', autor=user, is_active=True)
        contents['Edicion'] = Content.objects.filter(state='revision', autor=user, is_active=True)
        contents['A publicar'] = Content.objects.filter(state='to_publish', autor=user, is_active=True)
        contents['Publicado'] = Content.objects.filter(state='publish', autor=user, is_active=True)
        contents['Inactivo'] = Content.objects.filter(state='inactive', autor=user, is_active=True)
    elif user.has_perm('app.edit_content') or user.has_perm('app.publish_content') or user.has_perm('app.edit_is_active'):
        # Los editores y publicadores ven todos los contenidos activos sin importar el autor
        contents['Borrador'] = Content.objects.filter(state='draft', is_active=True)
        contents['Edicion'] = Content.objects.filter(state='revision', is_active=True)
        contents['A publicar'] = Content.objects.filter(state='to_publish', is_active=True)
        contents['Publicado'] = Content.objects.filter(state='publish', is_active=True)
        contents['Inactivo'] = Content.objects.filter(state='inactive', is_active=True)

    # Pasar permisos al contexto de la plantilla
    context = {
        'contents': contents,
        'can_create_content': user.has_perm('app.create_content'),
        'can_edit_content': user.has_perm('app.edit_content'),
        'can_publish_content': user.has_perm('app.publish_content'),
        'can_edit_is_active': user.has_perm('app.edit_is_active'),
    }
    return render(request, 'kanban/kanban_board.html', context)


# API para actualizar el estado
@csrf_exempt
@login_required
def update_content_state(request, content_id):
    user = request.user
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        new_state = data.get('state')

        # Verificar los estados válidos según los permisos
        if user.has_perm('app.create_content'):
            # Permite mover de 'Borrador' a 'Edición', de 'Publicado' a 'Inactivo', viceversa, y al mismo estado
            if content.autor == user:
                if (
                    (content.state == 'draft' and new_state == 'revision') or
                    (content.state == 'publish' and new_state == 'inactive') or
                    (content.state == 'inactive' and new_state == 'publish' and timezone.now() < content.date_expire) or
                    (content.state == new_state)  # Permite mover al mismo estado
                ):
                    content.state = new_state
                    content.save()
                    return JsonResponse({'status': 'success'})
                elif content.state == 'inactive' and new_state == 'publish' and timezone.now() >= content.date_expire:
                    return JsonResponse({'status': 'error', 'message': 'No se puede publicar un contenido expirado.'}, status=403)
                # Restricción para pasar de 'Borrador' a 'Publicado' si la categoría no es moderada
                elif content.state == 'draft' and new_state == 'publish':
                    if not content.category.is_moderated:
                        content.state = new_state
                        content.date_published = timezone.now()
                        content.save()
                        return JsonResponse({'status': 'success'})
                    else:
                        return JsonResponse({'status': 'error',
                                             'message': 'No se puede publicar un contenido de categoría moderada desde el estado de Borrador.'},
                                            status=403)

        elif user.has_perm('app.edit_content'):
            # Permite mover de 'Edición' a 'A publicar' y al mismo estado
            if (content.state == 'revision' and new_state == 'to_publish') or (content.state == new_state):
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})

        elif user.has_perm('app.publish_content'):
            # Permite mover de 'A publicar' a 'Publicado', 'Revisión' y al mismo estado
            if content.state == 'to_publish' and new_state in ['publish', 'revision', 'to_publish'] or (content.state == new_state):
                if new_state == 'publish' and  content.state != 'publish':
                    content.date_published = timezone.now()
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})

        elif user.has_perm('app.edit_is_active'):
            # Permite mover de 'Publicado' a 'Inactivo' y desactiva el contenido
            if content.state == 'publish' and new_state == 'inactive' or (content.state == new_state):
                content.state = new_state
                # content.is_active = False
                content.save()
                return JsonResponse({'status': 'success'})

        # Responder con un error si la acción no está permitida
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}, status=403)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

class ContentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = '/tablero/' # a donde ir despues
    permission_required = 'app.create_content'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Elimina el campo 'change_reason' para que no se muestre en el formulario de creación
        del form.fields['change_reason']
        return form

    def form_valid(self, form):
        content = form.save(commit=False)
        content.autor = self.request.user
        content.is_active = True
        content.date_create = timezone.now()
        content.date_expire = None
        content.state = Content.StateChoices.draft
        content.save()

        # Guarda las relaciones M2M (tags)
        form.save_m2m()

        # Establece la razón de cambio en el historial como 'Creación de contenido'
        update_change_reason(content, 'Creación de contenido')

        messages.success(self.request, 'Contenido modificado exitosamente')
        return redirect(self.success_url)
        
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    model = Content
    form_class = ContentForm
    template_name = 'content/content_form.html'
    success_url = '/tablero/'

    # Lista de permisos
    required_permissions = ['app.create_content', 'app.edit_content']

    def dispatch(self, request, *args, **kwargs):
        # Verifica si el usuario tiene al menos uno de los permisos requeridos
        if not any(request.user.has_perm(perm) for perm in self.required_permissions):
            raise PermissionDenied

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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.get_object().state == Content.StateChoices.draft:
            del form.fields['change_reason']
        return form
    
    def form_valid(self, form):
        user = self.request.user

        # Recupera el objeto original desde la base de datos
        content = self.get_object()

        change_reason = None

        if user.id == content.autor_id and user.has_perm('app.create_content') and content.state == Content.StateChoices.draft:
        # Si el usuario es el autor del contenido. tiene permisos de autoria y el cotenido está en estado borrador, OK
            form_data = form.cleaned_data
            for field in form_data:
                setattr(content, field, form_data[field])

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

        # Guarda las relaciones manualmente para el campo 'tags'


        # Actualiza la razón de cambio en el historial


        messages.success(self.request, 'Contenido modificado exitosamente.')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        return super().form_invalid(form)


def view_content(request, id):
    content = get_object_or_404(Content, id=id)
    #Traer la historia y renderizarla de manera descendente
    history = content.history.all().order_by('-history_date')
    return render(request, 'content/view.html', {"content" : content, "history" : history})

def view_version(request, content_id, history_id):
    content = get_object_or_404(Content, id=content_id)
    history = content.history.filter(history_id=history_id).first()

    if not history:
        raise Http404
    return render(request, 'content/view_version.html', {"content" : content, "history" : history})
