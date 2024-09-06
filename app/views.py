from django.contrib.auth import login, authenticate
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

from category.models import Category
from content.models import Content
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser


# Create your views here.

def home_view(request):
    cat_query = request.GET.get('cat')
    category = None
    autor_query = request.GET.get('autor')
    autor = None
    contents = Content.objects.filter(is_active=True).select_related('category', 'autor').order_by('-date_create')
    if cat_query:
        category = Category.objects.get(id=cat_query)
        contents = contents.filter(category_id=cat_query)
    if autor_query:
        autor = CustomUser.objects.get(id=autor_query)
    paginator = Paginator(contents, 10)
    str_page_number = request.GET.get('page')
    if str_page_number is None or str_page_number == '':
        page_number = 1
    else:
        page_number = int(str_page_number)
    if (page_number is None) or (page_number < 1): page_number = 1
    page_obj = paginator.get_page(page_number)
    return render(request, 'inicio.html', {'page_obj': page_obj, 'category': category, 'autor': autor})
