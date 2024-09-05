from unicodedata import category

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404

from category.models import Category
from content.models import Content


# Create your views here.
def content_by_category_view(request, id):
    category = get_object_or_404(Category, id=id)
    contents = Content.objects.filter(
        is_active=True,
        category=category,
    ).select_related('category', 'autor').order_by('-date_create')
    paginator = Paginator(contents, 10)
    str_page_number = request.GET.get('page')
    if str_page_number is None or str_page_number == '':
        page_number = 1
    else:
        page_number = int(str_page_number)
    if (page_number is None) or (page_number < 1): page_number = 1
    page_obj = paginator.get_page(page_number)
    return render(request, 'category/content_by_category.html', {'page_obj': page_obj, 'category': category})
