from decouple import config
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from app.forms import CustomAuthenticationForm, CustomUserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import login, authenticate
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
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
    logout(request)
    messages.success(request, '¡Sesión cerrada exitosamente!')
    return redirect('/')


def reset_password_view(request):
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

            # Renderizar el email
            email_subject = 'Restablecimiento de contraseña'
            email_body = render_to_string('password_reset_email.html', {'reset_link': reset_link})

            # Enviar el correo electrónico
            send_mail(
                email_subject,
                '',
                config('EMAIL_HOST_USER'),  # Puedes personalizar esto o usar DEFAULT_FROM_EMAIL
                [user.email],
                fail_silently=False,
                html_message=email_body,
            )

            messages.success(request, "¡Envío de correo electrónico de recuperación exitoso!")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect('password_reset')
    else:
        form = PasswordResetForm()
    return render(request, 'password-reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
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
                return render(request, 'password_reset_confirm.html', {'form': form})
        else:
            form = SetPasswordForm()

    else:
        messages.error(request, "El enlace de restablecimiento de contraseña no es válido.")
        return redirect('login')

    return render(request, 'password_reset_confirm.html', {'form': form})
