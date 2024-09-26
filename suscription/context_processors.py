from django.apps import apps


def suscriptions(request):
    suscription_model = apps.get_model('suscription', 'Suscription')

    if request.user.is_authenticated:
        user_suscriptions = suscription_model.objects.filter(user=request.user, state='active').values_list('category_id', flat=True)
    else:
        user_suscriptions = []

    # Retorna un diccionario con las categorías filtradas por tipo
    return {
        'user_suscriptions': user_suscriptions
    }
