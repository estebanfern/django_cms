from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from app.forms import ProfileUpdateForm


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            print(form.errors)
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'profile/profile.html', {'form': form})
