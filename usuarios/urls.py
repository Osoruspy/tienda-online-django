from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro_cliente, name='registro'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('redireccion-despues-login/', views.redireccion_despues_login, name='redireccion_login'),
    
    # Login con redirección personalizada
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    
    # Logout
    path('logout/', auth_views.LogoutView.as_view(
        template_name='registration/logout.html',
    ), name='logout'),
]