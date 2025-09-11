from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.lista_productos, name='lista'),
    path('categoria/<slug:slug_categoria>/', views.por_categoria, name='por_categoria'),
    path('<slug:slug>/', views.detalle_producto, name='detalle'),
]