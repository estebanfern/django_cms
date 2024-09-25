from django.urls import path
from . import views

app_name = 'content'  # Define el app_name para usarlo como namespace

urlpatterns = [
    path('report/<int:report_id>/', views.report_detail, name='report-detail'),
    # Otras rutas...
]
