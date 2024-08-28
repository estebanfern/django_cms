from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Create your views here.

def home_view(request):
    return render(request, 'inicio.html')

