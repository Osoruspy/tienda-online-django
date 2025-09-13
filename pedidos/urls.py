from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    # URLs para clientes
    path('', views.lista_pedidos, name='lista'),
    path('crear/', views.crear_pedido_desde_carrito, name='crear_desde_carrito'),
    path('confeccion/crear/', views.crear_pedido_confeccion, name='crear_confeccion'),
    path('<int:pedido_id>/', views.detalle_pedido, name='detalle'),
    path('<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar'),
    
    # URLs para empleados/administradores
    path('gestion/', views.gestion_pedidos, name='gestion'),
    path('<int:pedido_id>/cambiar-estado/', views.cambiar_estado_pedido, name='cambiar_estado'),

    # URLs de Checkout
    path('checkout/', views.proceso_checkout, name='checkout'),
    path('checkout/completado/<int:pedido_id>/', views.checkout_completado, name='checkout_completado'),
]