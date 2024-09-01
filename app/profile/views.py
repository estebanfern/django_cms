from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from app.forms import ProfileUpdateForm, ChangePasswordForm
from app.models import CustomUser

@login_required
def profile_view(request):
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
    user_profile = get_object_or_404(CustomUser, id=id)
    return render(request, 'profile/view_profile.html', {'user_profile' : user_profile})
