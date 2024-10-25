from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.datetime_safe import datetime

from app.models import CustomUser
from category.models import Category
from content.models import Content
from django.contrib.auth.models import Permission
from django.db.models import Q

@login_required
def view_stadistics(request):
    """
    Muestra la vista de estadísticas con opciones para filtrar usuarios y categorías.

    :param request: Objeto de solicitud HTTP.
    :type request: HttpRequest

    :comportamiento:
        - Verifica los permisos del usuario para acceder a las estadísticas.
        - Filtra los usuarios según los permisos y el usuario autenticado.
        - Obtiene todas las categorías.
        - Establece los filtros de usuario, categoría y fechas de inicio y fin basados en los parámetros de la solicitud.

    :return: Respuesta renderizada con la plantilla de estadísticas y datos de filtros.
    :rtype: HttpResponse
    """

    user = request.user
    users = []
    if user.has_perm('app.view_stadistics'):
        permiso = Permission.objects.get(codename='create_content')
        users = CustomUser.objects.filter(
            Q(user_permissions=permiso) | Q(groups__permissions=permiso)
        ).distinct()
    elif user.has_perm('app.create_content'):
        users = CustomUser.objects.filter(id=user.id)
    else:
        raise PermissionError('No tiene permisos para acceder a esta vista')
    categories = Category.objects.all()
    usr = int(request.GET.get('users')) if request.GET.get('users') else 0
    cat = int(request.GET.get('categories')) if request.GET.get('categories') else 0
    date_begin = request.GET.get('date_begin') if request.GET.get('date_begin') else None
    date_end = request.GET.get('date_end') if request.GET.get('date_end') else None
    return render(request, 'stadistic/view_stadistics.html',{'users': users, 'categories': categories, 'usr': usr, 'cat': cat, 'date_begin': date_begin, 'date_end': date_end})

@login_required
# @permission_required('app.create_content', raise_exception=True)
def top_liked(request):
    """
    Devuelve los 10 contenidos con más "me gusta" del autor autenticado en formato JSON.


    :param request: Objeto de solicitud HTTP realizado por el usuario autenticado.
    :type request: HttpRequest

    :comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con más "me gusta", incluyendo los campos: título, número de "me gusta", fecha de creación y fecha de publicación.
        - Ordena los resultados por el número de "me gusta" en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    :return: Respuesta con los datos de los contenidos más valorados en formato JSON.
    :rtype: JsonResponse
    """
    user = request.user

    if request.GET.get('users'):
        top_contents = Content.objects.filter(autor_id=int(request.GET.get('users')))
    else:
        top_contents = Content.objects.all()

    if request.GET.get('categories'):
        top_contents = top_contents.filter(category_id=int(request.GET.get('categories')))

    if request.GET.get('date_begin'):
        date_begin_str = request.GET.get('date_begin')  # Por ejemplo, '2024-10-17'
        date_begin = datetime.strptime(date_begin_str, '%Y-%m-%dT%H:%M')
        date_begin = timezone.make_aware(date_begin, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__gte=date_begin)

    if request.GET.get('date_end'):
        date_end_str = request.GET.get('date_end')  # Por ejemplo, '2024-10-22'
        date_end = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M')
        date_end = timezone.make_aware(date_end, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__lte=date_end)

    top_contents = top_contents.filter(state=Content.StateChoices.publish, date_published__lt=timezone.now())\
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
# @permission_required('app.create_content', raise_exception=True)
def top_disliked(request):
    """
    Devuelve los 10 contenidos con más "no me gusta" del autor autenticado en formato JSON.

    :param request: Objeto de solicitud HTTP realizado por el usuario autenticado.
    :type request: HttpRequest

    :comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con más "no me gusta", incluyendo los campos: título, número de "no me gusta", fecha de creación y fecha de publicación.
        - Ordena los resultados por el número de "no me gusta" en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    :return: Respuesta con los datos de los contenidos más rechazados en formato JSON.
    :rtype: JsonResponse
    """

    user = request.user

    if request.GET.get('users'):
        top_contents = Content.objects.filter(autor_id=int(request.GET.get('users')))
    else:
        top_contents = Content.objects.all()

    if request.GET.get('categories'):
        top_contents = top_contents.filter(category_id=int(request.GET.get('categories')))
    else:
        top_contents = top_contents

    if request.GET.get('date_begin'):
        date_begin_str = request.GET.get('date_begin')  # Por ejemplo, '2024-10-17'
        date_begin = datetime.strptime(date_begin_str, '%Y-%m-%dT%H:%M')
        date_begin = timezone.make_aware(date_begin, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__gte=date_begin)

    if request.GET.get('date_end'):
        date_end_str = request.GET.get('date_end')  # Por ejemplo, '2024-10-22'
        date_end = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M')
        date_end = timezone.make_aware(date_end, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__lte=date_end)

    top_contents = top_contents.filter(state=Content.StateChoices.publish, date_published__lt=timezone.now())\
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
# @permission_required('app.create_content', raise_exception=True)
def top_rating(request):
    """
    Devuelve los 10 contenidos mejor valorados del autor autenticado en formato JSON.

    :param request: Objeto de solicitud HTTP realizado por el usuario autenticado.
    :type request: HttpRequest

    :comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con el promedio de calificaciones más alto, incluyendo los campos: título, promedio de calificaciones, fecha de creación y fecha de publicación.
        - Ordena los resultados por el promedio de calificaciones en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    :return: Respuesta con los datos de los contenidos mejor valorados en formato JSON.
    :rtype: JsonResponse
    """

    user = request.user

    if request.GET.get('users'):
        top_contents = Content.objects.filter(autor_id=int(request.GET.get('users')))
    else:
        top_contents = Content.objects.all()

    if request.GET.get('categories'):
        top_contents = top_contents.filter(category_id=int(request.GET.get('categories')))
    else:
        top_contents = top_contents

    if request.GET.get('date_begin'):
        date_begin_str = request.GET.get('date_begin')  # Por ejemplo, '2024-10-17'
        date_begin = datetime.strptime(date_begin_str, '%Y-%m-%dT%H:%M')
        date_begin = timezone.make_aware(date_begin, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__gte=date_begin)

    if request.GET.get('date_end'):
        date_end_str = request.GET.get('date_end')  # Por ejemplo, '2024-10-22'
        date_end = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M')
        date_end = timezone.make_aware(date_end, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__lte=date_end)

    top_contents = top_contents.filter(state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
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
# @permission_required('app.create_content', raise_exception=True)
def top_view(request):
    """
    Devuelve los 10 contenidos más vistos del autor autenticado en formato JSON.

    :param request: Objeto de solicitud HTTP realizado por el usuario autenticado.
    :type request: HttpRequest

    :comportamiento:
        - Filtra los contenidos publicados creados por el usuario autenticado.
        - Obtiene los 10 contenidos con más vistas, incluyendo los campos: título, número de vistas, fecha de creación y fecha de publicación.
        - Ordena los resultados por el número de vistas en orden descendente.
        - Retorna los datos en formato JSON con el estado de éxito.

    :return: Respuesta con los datos de los contenidos más vistos en formato JSON.
    :rtype: JsonResponse
    """

    user = request.user

    if request.GET.get('users'):
        top_contents = Content.objects.filter(autor_id=int(request.GET.get('users')))
    else:
        top_contents = Content.objects.all()

    if request.GET.get('categories'):
        top_contents = top_contents.filter(category_id=int(request.GET.get('categories')))
    else:
        top_contents = top_contents

    if request.GET.get('date_begin'):
        date_begin_str = request.GET.get('date_begin')  # Por ejemplo, '2024-10-17'
        date_begin = datetime.strptime(date_begin_str, '%Y-%m-%dT%H:%M')
        date_begin = timezone.make_aware(date_begin, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__gte=date_begin)

    if request.GET.get('date_end'):
        date_end_str = request.GET.get('date_end')  # Por ejemplo, '2024-10-22'
        date_end = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M')
        date_end = timezone.make_aware(date_end, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__lte=date_end)

    top_contents = top_contents.filter(state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
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
# @permission_required('app.create_content', raise_exception=True)
def top_shares(request):
    """
        Devuelve los 10 contenidos más compartidos del autor autenticado en formato JSON.

        :param request: Objeto de solicitud HTTP realizado por el usuario autenticado.
        :type request: HttpRequest

        :comportamiento:
            - Filtra los contenidos publicados creados por el usuario autenticado.
            - Obtiene los 10 contenidos con más compartidos, incluyendo los campos: título, número de compartidos, fecha de creación y fecha de publicación.
            - Ordena los resultados por el número de compartidos en orden descendente.
            - Retorna los datos en formato JSON con el estado de éxito.

        :return: Respuesta con los datos de los contenidos más compartidos en formato JSON.
        :rtype: JsonResponse
        """
    user = request.user

    if request.GET.get('users'):
        top_contents = Content.objects.filter(autor_id=int(request.GET.get('users')))
    else:
        top_contents = Content.objects.all()

    if request.GET.get('categories'):
        top_contents = top_contents.filter(category_id=int(request.GET.get('categories')))
    else:
        top_contents = top_contents

    if request.GET.get('date_begin'):
        date_begin_str = request.GET.get('date_begin')  # Por ejemplo, '2024-10-17'
        date_begin = datetime.strptime(date_begin_str, '%Y-%m-%dT%H:%M')
        date_begin = timezone.make_aware(date_begin, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__gte=date_begin)

    if request.GET.get('date_end'):
        date_end_str = request.GET.get('date_end')  # Por ejemplo, '2024-10-22'
        date_end = datetime.strptime(date_end_str, '%Y-%m-%dT%H:%M')
        date_end = timezone.make_aware(date_end, timezone.get_current_timezone())
        top_contents = top_contents.filter(date_published__lte=date_end)

    top_contents = top_contents.filter(state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
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
