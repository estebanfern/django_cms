from django.apps import apps


def categories(request):
    category_model = apps.get_model('category', 'Category')
    return {
        'categories_publicas': category_model.objects.filter(type='Publico'),
        'categories_suscriptores': category_model.objects.filter(type='Suscriptor'),
        'categories_pago': category_model.objects.filter(type='Pago'),
    }
