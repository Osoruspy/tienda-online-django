from django.urls import path
from . import views

app_name = 'confecciones'

urlpatterns = [
    # URLs para clientes
    path('pedido/<int:pedido_id>/detalle/', views.crear_detalle_confeccion, name='crear_detalle'),
    path('detalle/<int:detalle_id>/items/', views.agregar_item_adicional, name='agregar_item_adicional'),
    path('<int:confeccion_id>/finalizar/', views.finalizar_confeccion, name='finalizar'),
    path('<int:confeccion_id>/', views.detalle_confeccion, name='detalle'),
    
    # URLs para empleados
    path('gestion/', views.gestion_confecciones, name='gestion'),
    path('<int:confeccion_id>/cambiar-estado/', views.cambiar_estado_confeccion, name='cambiar_estado'),
    path('<int:confeccion_id>/asignar/', views.asignar_confeccion, name='asignar'),
]