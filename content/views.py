from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Content
import json
from django.contrib.auth.decorators import login_required

@login_required
def kanban_board(request):
    user = request.user
    contents = {
        'Borrador': [],
        'Edición': [],
        'A publicar': [],
        'Publicado': [],
        'Inactivo': [],
    }

    # Filtrar contenidos según los permisos del usuario y que estén activos
    if user.has_perm('app.create_content'):
        # Los autores ven solo sus contenidos activos en cualquier estado
        contents['Borrador'] = Content.objects.filter(state='draft', autor=user, is_active=True)
        contents['Edición'] = Content.objects.filter(state='revision', autor=user, is_active=True)
        contents['A publicar'] = Content.objects.filter(state='to_publish', autor=user, is_active=True)
        contents['Publicado'] = Content.objects.filter(state='publish', autor=user, is_active=True)
        contents['Inactivo'] = Content.objects.filter(state='inactive', autor=user, is_active=True)
    elif user.has_perm('app.edit_content') or user.has_perm('app.publish_content') or user.has_perm('app.edit_is_active'):
        # Los editores y publicadores ven todos los contenidos activos sin importar el autor
        contents['Borrador'] = Content.objects.filter(state='draft', is_active=True)
        contents['Edición'] = Content.objects.filter(state='revision', is_active=True)
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

        elif user.has_perm('app.edit_content'):
            # Permite mover de 'Edición' a 'A publicar' y al mismo estado
            if (content.state == 'revision' and new_state == 'to_publish') or (content.state == new_state):
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})

        elif user.has_perm('app.publish_content'):
            # Permite mover de 'A publicar' a 'Publicado', 'Revisión' y al mismo estado
            if content.state == 'to_publish' and new_state in ['publish', 'revision', 'to_publish']:
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})

        elif user.has_perm('app.edit_is_active'):
            # Permite mover de 'Publicado' a 'Inactivo' y desactiva el contenido
            if content.state == 'publish' and new_state == 'inactive':
                content.state = new_state
                # content.is_active = False
                content.save()
                return JsonResponse({'status': 'success'})

        # Responder con un error si la acción no está permitida
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}, status=403)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)