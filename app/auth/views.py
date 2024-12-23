from django.contrib.auth import logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from notification.tasks import send_notification_task

import notification.service
from app.forms import CustomAuthenticationForm, CustomUserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate
from django.contrib import messages

def register_view(request):
    """
    Vista para el registro de nuevos usuarios.

    Si el método de solicitud es POST, se procesa el formulario de creación de usuario.
    Si el formulario es válido, se guarda el nuevo usuario y se inicia sesión automáticamente.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :return: Redirige a la página de inicio si el registro es exitoso o renderiza la página de registro con el formulario correspondiente.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            notification.service.welcomeUser(user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """
    Vista para el inicio de sesión de usuarios.

    Si el método de solicitud es POST, se procesa el formulario de autenticación.
    Si el formulario es válido, se inicia sesión del usuario.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :return: Redirige a la página de inicio si el inicio de sesión es exitoso o renderiza la página de inicio de sesión con el formulario correspondiente.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, '¡Inicio de sesión exitoso!')
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """
    Vista para cerrar la sesión del usuario actual.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :return: Redirige a la página principal después de cerrar la sesión.
    :rtype: HttpResponse
    """
    logout(request)
    messages.success(request, '¡Sesión cerrada exitosamente!')
    return redirect('/')


def reset_password_view(request):
    """
    Vista para solicitar el restablecimiento de la contraseña del usuario.

    Si el método de solicitud es POST, se procesa el formulario de restablecimiento de contraseña.
    Si el formulario es válido, se envía un correo electrónico al usuario con un enlace para restablecer la contraseña.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :return: Redirige a la página de inicio de sesión después de enviar el correo o renderiza la página de restablecimiento de contraseña con el formulario correspondiente.
    :rtype: HttpResponse
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = get_user_model().objects.get(email=form.cleaned_data['email'])

            # Generar el token y el UID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Crear el enlace de recuperación de contraseña
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            # Enviar el email
            email_subject = 'Restablecimiento de contraseña'
            template='email/password_reset_email.html'
            context = {
                "reset_link": reset_link
            }
            send_notification_task.delay(email_subject, [user.email], context, template)
            messages.success(request, "¡Envío de correo electrónico de recuperación exitoso!")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect('password_reset')
    else:
        form = PasswordResetForm()
    return render(request, 'email/../../templates/password-reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
    """
    Vista para confirmar el restablecimiento de la contraseña mediante un enlace enviado al correo electrónico del usuario.

    Valida el token y el UID del usuario para permitir el cambio de contraseña.
    Si la validación es exitosa, permite al usuario establecer una nueva contraseña.

    :param request: La solicitud HTTP recibida.
    :type request: HttpRequest
    :param uidb64: El UID del usuario codificado en base64.
    :type uidb64: str
    :param token: El token de seguridad para confirmar la validez del enlace.
    :type token: str
    :return: Redirige a la página de inicio de sesión si la actualización es exitosa o renderiza la página de confirmación de restablecimiento de contraseña con el formulario correspondiente.
    :rtype: HttpResponse
    """
    user_model = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                messages.success(request, "¡Contraseña actualizada con éxito!")
                return redirect('login')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
                return render(request, 'email/../../templates/password_reset_confirm.html', {'form': form})
        else:
            form = SetPasswordForm()

    else:
        messages.error(request, "El enlace de restablecimiento de contraseña no es válido.")
        return redirect('login')

    return render(request, 'email/../../templates/password_reset_confirm.html', {'form': form})
