from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from content.models import Content

@login_required
@permission_required('app.create_content', raise_exception=True)
def view_stadistics(request):
    return render(request, 'stadistic/view_stadistics.html')

@login_required
@permission_required('app.create_content', raise_exception=True)
def top_liked(request):
    """
    Devuelve los 10 contenidos con más "me gusta" del autor autenticado en formato JSON.

    Requiere:
        El usuario debe estar autenticado.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP realizado por el usuario autenticado.

    Comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con más "me gusta", incluyendo los campos: título, número de "me gusta", fecha de creación y fecha de publicación.
        - Ordena los resultados por el número de "me gusta" en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    Retorna:
        JsonResponse: Respuesta con los datos de los contenidos más valorados en formato JSON.
    """

    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now())\
                                    .values('title', 'likes_count', 'date_create', 'date_published')\
                                    .order_by('-likes_count')[:10]
    data =  {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
                data,
                safe=False
            )

@login_required
@permission_required('app.create_content', raise_exception=True)
def top_disliked(request):
    """
    Devuelve los 10 contenidos con más "no me gusta" del autor autenticado en formato JSON.

    Requiere:
        El usuario debe estar autenticado.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP realizado por el usuario autenticado.

    Comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con más "no me gusta", incluyendo los campos: título, número de "no me gusta", fecha de creación y fecha de publicación.
        - Ordena los resultados por el número de "no me gusta" en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    Retorna:
        JsonResponse: Respuesta con los datos de los contenidos más rechazados en formato JSON.
    """

    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now())\
                                    .values('title', 'dislikes_count', 'date_create', 'date_published')\
                                    .order_by('-dislikes_count')[:10]
    data =  {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
                data,
                safe=False
            )

@login_required
@permission_required('app.create_content', raise_exception=True)
def top_rating(request):
    """
    Devuelve los 10 contenidos mejor valorados del autor autenticado en formato JSON.

    Requiere:
        El usuario debe estar autenticado.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP realizado por el usuario autenticado.

    Comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con el promedio de calificaciones más alto, incluyendo los campos: título, promedio de calificaciones, fecha de creación y fecha de publicación.
        - Ordena los resultados por el promedio de calificaciones en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    Retorna:
        JsonResponse: Respuesta con los datos de los contenidos mejor valorados en formato JSON.
    """

    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
                                    .values('title', 'rating_avg', 'date_create', 'date_published') \
                                    .order_by('-rating_avg')[:10]
    data = {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
        data,
        safe=False
    )

@login_required
@permission_required('app.create_content', raise_exception=True)
def top_view(request):
    """
    Devuelve los 10 contenidos más vistos del autor autenticado en formato JSON.

    Requiere:
        El usuario debe estar autenticado.

    Parámetros:
        request (HttpRequest): Objeto de solicitud HTTP realizado por el usuario autenticado.

    Comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con más vistas, incluyendo los campos: título, número de vistas, fecha de creación y fecha de publicación.
        - Ordena los resultados por el número de vistas en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    Retorna:
        JsonResponse: Respuesta con los datos de los contenidos más vistos en formato JSON.
    """

    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
                                    .values('title', 'views_count', 'date_create', 'date_published') \
                                    .order_by('-views_count')[:10]
    data = {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
        data,
        safe=False
    )

@login_required
@permission_required('app.create_content', raise_exception=True)
def top_shares(request):
    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
                       .values('title', 'shares_count', 'date_create', 'date_published') \
                       .order_by('-shares_count')[:10]
    data = {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
        data,
        safe=False
    )
