from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from app.forms import ProfileUpdateForm, ChangePasswordForm
from app.models import CustomUser

@login_required
def profile_view(request):
    """
    Vista para la actualización del perfil del usuario autenticado.

    Si el método de solicitud es POST, procesa el formulario de actualización del perfil.
    Si el formulario es válido, guarda los cambios en el perfil del usuario.
    También proporciona un formulario para cambiar la contraseña del usuario.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :return: Redirige a la vista de perfil después de actualizarlo o renderiza la página de perfil con el formulario de actualización y el formulario de cambio de contraseña.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ProfileUpdateForm(instance=request.user)
    password_form = ChangePasswordForm(request.user)
    return render(request, 'profile/profile.html', {'form': form, 'password_form': password_form})

@login_required
def change_password(request):
    """
    Vista para cambiar la contraseña del usuario autenticado.

    Si el método de solicitud es POST, procesa el formulario de cambio de contraseña.
    Si el formulario es válido, cambia la contraseña del usuario y muestra un mensaje de éxito.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :return: Redirige a la página de inicio de sesión si el cambio de contraseña es exitoso o redirige a la vista de perfil si el formulario contiene errores.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        password_form = ChangePasswordForm(request.user, request.POST)
        if password_form.is_valid():
            password_form.save()
            messages.success(request, '¡Contraseña cambiada exitosamente!')
            return redirect('login')
        else:
            for field, errors in password_form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect('profile')
    return redirect('profile')

def other_profile_view(request, id):
    """
    Vista para mostrar el perfil de otro usuario.

    Obtiene el perfil de un usuario específico basado en su ID.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :param id: El ID del usuario cuyo perfil se desea mostrar.
    :type id: int
    :return: Renderiza la página del perfil del usuario especificado.
    :rtype: HttpResponse
    """
    user_profile = get_object_or_404(CustomUser, id=id)
    return render(request, 'profile/view_profile.html', {'user_profile' : user_profile})
