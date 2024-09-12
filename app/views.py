from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from category.models import Category
from content.models import Content



# Create your views here.

def home_view(request):
    cat_query = request.GET.get('cat')
    category = None
    query = request.GET.get('query')
    contents = Content.objects.filter(is_active=True, state=Content.StateChoices.publish).select_related('category', 'autor').order_by('-date_create')
    if cat_query:
        category = Category.objects.get(id=cat_query)
        contents = contents.filter(category_id=cat_query)
    if query:
        contents = contents.filter(
            Q(title__icontains=query) | Q(autor__name__icontains=query)
        )
    paginator = Paginator(contents, 10)
    str_page_number = request.GET.get('page')
    if str_page_number is None or str_page_number == '':
        page_number = 1
    else:
        page_number = int(str_page_number)
    if (page_number is None) or (page_number < 1): page_number = 1
    page_obj = paginator.get_page(page_number)
    return render(request, 'inicio.html', {'page_obj': page_obj, 'category': category, 'query': query})
