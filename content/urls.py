from django.urls import path
from content.admin import ContentAdmin
from . import views

app_name = 'content'  

urlpatterns = [
    path('report/<int:report_id>/', views.report_detail, name='report-detail'),
    path('admin/content/<int:content_id>/view/', views.view_content_detail, name='view_content_detail'),  
]
