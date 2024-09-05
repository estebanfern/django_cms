"""
URL configuration for cms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

Examples:

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from content.views import kanban_board, update_content_state

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

from django.contrib import admin
from django.urls import path
from app.auth.views import register_view, login_view, logout_view, reset_password_view, password_reset_confirm_view
from app.profile.views import other_profile_view, profile_view, change_password
from app.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', home_view, name='home'),

    #Auth
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', reset_password_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    #############aaaaaa
    # path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    # path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    # path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    # path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    #####aaaaaaaaaaaaaaaaa

    # Profile
    path('profile/', profile_view, name='profile'),
    path('profile/<int:id>/', other_profile_view, name='profile_view'),
    path('change-password/', change_password, name='change_password'),

    path('tablero/', kanban_board, name='kanban_board'),
    path('api/update-content-state/<int:content_id>/', update_content_state, name='update_content_state'),
]

