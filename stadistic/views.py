from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from content.models import Content

@login_required
def view_stadistics(request):
    return render(request, 'stadistic/view_stadistics.html')

@login_required
def top_liked(request):
    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now())\
                                    .values('title', 'likes_count', 'date_create', 'date_published')\
                                    .order_by('-likes_count')[:10]
    data =  {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
                data,
                safe=False
            )

@login_required
def top_disliked(request):
    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now())\
                                    .values('title', 'dislikes_count', 'date_create', 'date_published')\
                                    .order_by('-dislikes_count')[:10]
    data =  {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
                data,
                safe=False
            )

@login_required
def top_rating(request):
    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
                                    .values('title', 'rating_avg', 'date_create', 'date_published') \
                                    .order_by('-rating_avg')[:10]
    data = {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
        data,
        safe=False
    )

@login_required
def top_view(request):
    user = request.user
    top_contents = Content.objects.filter(autor=user, state=Content.StateChoices.publish, date_published__lt=timezone.now()) \
                                    .values('title', 'views_count', 'date_create', 'date_published') \
                                    .order_by('-views_count')[:10]
    data = {
        'status': 'success',
        'result': list(top_contents)
    }
    return JsonResponse(
        data,
        safe=False
    )