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

    # Filtrar contenidos según el rol del usuario
    if user.groups.filter(name='Autor').exists():
        # El autor ve solo sus contenidos en cualquier estado
        contents['Borrador'] = Content.objects.filter(state='draft', autor=user)
        contents['Edición'] = Content.objects.filter(state='revision', autor=user)
        contents['A publicar'] = Content.objects.filter(state='to_publish', autor=user)
        contents['Publicado'] = Content.objects.filter(state='publish', autor=user)
        contents['Inactivo'] = Content.objects.filter(state='inactive', autor=user)

    elif user.groups.filter(name__in=['Editor', 'Publicador']).exists():
        # Los editores y publicadores ven todos los contenidos sin importar el autor
        contents['Borrador'] = Content.objects.filter(state='draft')
        contents['Edición'] = Content.objects.filter(state='revision')
        contents['A publicar'] = Content.objects.filter(state='to_publish')
        contents['Publicado'] = Content.objects.filter(state='publish')
        contents['Inactivo'] = Content.objects.filter(state='inactive')

    return render(request, 'kanban/kanban_board.html', {'contents': contents})

# API para actualizar el estado
@csrf_exempt
@login_required
def update_content_state(request, content_id):
    user = request.user
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        new_state = data.get('state')

        # Verificar los estados válidos para cada rol
        if user.groups.filter(name='Autor').exists():
            # Los autores pueden mover sus contenidos de 'Borrador' a 'Revisión', 'Publicado' a 'Inactivo' y viceversa
            if content.autor == user and (
                (content.state == 'draft' and new_state in ['draft', 'revision']) or
                (content.state == 'publish' and new_state in ['publish', 'inactive']) or
                (content.state == 'inactive' and new_state in ['inactive', 'publish'])
            ):
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No tienes permiso para cambiar el estado.'}, status=403)

        elif user.groups.filter(name='Editor').exists():
            # El editor solo puede mover de 'Revisión' a 'A publicar' o confirmar el estado
            if content.state == 'revision' and new_state in ['revision', 'to_publish']:
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Cambio de estado no permitido.'}, status=403)

        elif user.groups.filter(name='Publicador').exists():
            # El publicador solo puede mover de 'A publicar' a 'Publicado', 'Revisión' o confirmar el estado
            if content.state == 'to_publish' and new_state in ['to_publish', 'publish', 'revision']:
                content.state = new_state
                content.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Cambio de estado no permitido.'}, status=403)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)
