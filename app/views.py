from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from content.models import Content
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
    # contents = Content.objects.filter(is_active=True).values('title', 'summary', 'category', 'autor', 'date_published')
    contents = Content.objects.filter(is_active=True).select_related('category', 'autor')
    paginator = Paginator(contents, 10)
    page_number = int(request.GET.get('page'))
    if (page_number is None) or (page_number < 1): page_number = 1
    page_obj = paginator.get_page(page_number)
    print(contents)
    return render(request, 'inicio.html', {'page_obj': page_obj})

