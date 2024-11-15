"""
Definición de rutas URL para la aplicación.

Esta lista de patrones de URL define las rutas accesibles en la aplicación,
incluyendo vistas de administración, autenticación, perfiles y restablecimiento de contraseñas.

Rutas:
    - 'admin/': Ruta para acceder al panel de administración de Django.
    - '': Ruta para la página de inicio, que utiliza la vista `home_view`.

    Autenticación (Auth):
    - 'register/': Ruta para el registro de usuarios, utilizando `register_view`.
    - 'login/': Ruta para el inicio de sesión de usuarios, utilizando `login_view`.
    - 'logout/': Ruta para cerrar la sesión de usuarios, utilizando `logout_view`.
    - 'password-reset/': Ruta para solicitar el restablecimiento de la contraseña, utilizando `reset_password_view`.
    - 'reset/<uidb64>/<token>/': Ruta para confirmar el restablecimiento de la contraseña, utilizando `password_reset_confirm_view`.

    Comentadas:
    - Las rutas comentadas corresponden a vistas de restablecimiento de contraseña basadas en clases de Django, 
    que pueden reemplazar a las vistas personalizadas si se desean utilizar las vistas predeterminadas de Django.

    Perfil (Profile):
    - 'profile/': Ruta para la vista del perfil del usuario autenticado, utilizando `profile_view`.
    - 'profile/<int:id>/': Ruta para la vista de perfil de otro usuario, utilizando `other_profile_view`.
    - 'change-password/': Ruta para cambiar la contraseña del usuario autenticado, utilizando `change_password`.
"""
from content.views import kanban_board, report_post, update_content_state, view_version, validate_permission_kanban_api, \
    like_content, dislike_content, view_count_share
from django.contrib import admin
from django.urls import include, path
from app.auth.views import register_view, login_view, logout_view, reset_password_view, password_reset_confirm_view
from app.profile.views import other_profile_view, profile_view, change_password
from app.views import *
from content.views import ContentCreateView, ContentUpdateView, view_content
from ckeditor_uploader import views
from django.conf import settings
from django.conf.urls.static import static
from category.views import categories_by_type
from rating import views as rating_views
from stadistic.views import view_stadistics, top_liked, top_rating, top_disliked, top_view, top_shares
from suscription.views import suscribe_category, unsuscribe_category, create_checkout_session, stripe_webhook, \
    my_subscriptions, finances, category_totals, category_timeline, daily_totals, table_data, export_to_excel

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', home_view, name='home'),

    #Auth
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', reset_password_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),

    # Profile
    path('profile/', profile_view, name='profile'),
    path('profile/<int:id>/', other_profile_view, name='profile_view'),
    path('change-password/', change_password, name='change_password'),

    # Content - Edit (Autor - Editor)
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path("content-upload/", views.upload, name="content_ckeditor_upload"),
    path('content/new/', ContentCreateView.as_view(), name='content-create'),
    path('content/<int:pk>/edit/', ContentUpdateView.as_view(), name='content-update'),
    path('content/<int:id>/', view_content, name='content_view'),
    path('content/<int:content_id>/history/<int:history_id>', view_version, name='view_content_version'),
    path('tablero/', kanban_board, name='kanban_board'),
    path('api/update-content-state/<int:content_id>/', update_content_state, name='update_content_state'),
    path('content/<int:pk>/edit/', ContentUpdateView.as_view(), name='edit_content'),
    path('report/<int:content_id>/', report_post, name='report_post'),  # Ruta para reportar
    path('api/validate-permission-kanban/', validate_permission_kanban_api, name='validate_permission_kanban_api'),

    # Content - Reactions
    path('like/<int:content_id>/', like_content, name='like_content'),
    path('dislike/<int:content_id>/', dislike_content, name='dislike_content'),

    # Rating
    path('rate/<int:content_id>/', rating_views.rate_content, name='rate_content'),

    # Share
    path('share/<int:content_id>/', view_count_share, name='share_content'),

    # Category
    path('category/<str:type>/', categories_by_type, name='categories_by_type'),
    # Category suscription
    path('category/<int:category_id>/suscribe/', suscribe_category, name='suscribe_category'),
    path('category/<int:category_id>/unsuscribe/', unsuscribe_category, name='unsuscribe_category'),
    path('create-checkout-session/<int:category_id>/', create_checkout_session, name='create_checkout_session'),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('subscriptions/', my_subscriptions, name='subscriptions'),

    #Stadistics
    path('stadistics/', view_stadistics, name='view_stadistics'),
    path('stadistics/likes/', top_liked, name='top_liked'),
    path('stadistics/dislikes/', top_disliked, name='top_disliked'),
    path('stadistics/rating/', top_rating, name='top_rating'),
    path('stadistics/views/', top_view, name='top_view'),
    path('stadistics/shares/', top_shares, name='top_shares'),

    path('finances/',finances, name='finances'),
    path('finances/category_totals/',category_totals, name='finances_category'),
    path('finances/category_timeline/', category_timeline, name='finances_category_timeline'),
    path('finances/daily_totals/', daily_totals, name='finances_daily_totals'),
    path('finances/table_data/', table_data, name='finances_table_data'),
    path('finances/export_to_excel/', export_to_excel, name='finances_export_to_excel'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
