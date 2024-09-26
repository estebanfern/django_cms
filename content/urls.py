from django.urls import path
from content.admin import ContentAdmin
from . import views

app_name = 'content'  # Define el app_name para usarlo como namespace

urlpatterns = [
    path('report/<int:report_id>/', views.report_detail, name='report-detail'),
    path('admin/content/<int:content_id>/view/', views.view_content_detail, name='view_content_detail'),  # Usa 'view_content_admin' como name

    # Otras rutas...
]
