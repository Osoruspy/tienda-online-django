from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path('', views.detalle_carrito, name='detalle'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar'),
    path('actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar'),
    path('eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar'),
    path('vaciar/', views.vaciar_carrito, name='vaciar'),
    path('transferir/', views.transferir_carrito_view, name='transferir'),
]