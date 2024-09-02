from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Create your views here.

def home_view(request):
    """
    Vista para la página de inicio.

    Renderiza la plantilla correspondiente a la página de inicio.

    Parámetros:
        request (HttpRequest): La solicitud HTTP recibida.

    Retorna:
        HttpResponse: Renderiza y devuelve la página de inicio ('inicio.html').
    """
    return render(request, 'inicio.html')

