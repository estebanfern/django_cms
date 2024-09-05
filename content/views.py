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

    # Filtrar contenidos según los permisos del usuario
    if user.has_perm('app.create_content'):
        contents['Borrador'] = Content.objects.filter(state='draft', autor=user)
        contents['Edición'] = Content.objects.filter(state='revision', autor=user)
        contents['A publicar'] = Content.objects.filter(state='to_publish', autor=user)
        contents['Publicado'] = Content.objects.filter(state='publish', autor=user)
        contents['Inactivo'] = Content.objects.filter(state='inactive', autor=user)
    elif user.has_perm('app.edit_content') or user.has_perm('app.publish_content'):
        contents['Borrador'] = Content.objects.filter(state='draft')
        contents['Edición'] = Content.objects.filter(state='revision')
        contents['A publicar'] = Content.objects.filter(state='to_publish')
        contents['Publicado'] = Content.objects.filter(state='publish')
        contents['Inactivo'] = Content.objects.filter(state='inactive')

    # Pasar permisos al contexto de la plantilla
    context = {
        'contents': contents,
        'can_create_content': user.has_perm('app.create_content'),
        'can_edit_content': user.has_perm('app.edit_content'),
        'can_publish_content': user.has_perm('app.publish_content'),
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
            # Permite mover de 'Borrador' a 'Edición', de 'Publicado' a 'Inactivo' y viceversa
            if content.autor == user and (
                (content.state == 'draft' and new_state == 'revision') or
                (content.state == 'publish' and new_state == 'inactive') or
                (content.state == 'inactive' and new_state == 'publish') or
                (content.state == new_state)
            ):
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})

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

        # Responder con un error si la acción no está permitida
        return JsonResponse({'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}, status=403)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)