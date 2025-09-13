from django.contrib import admin
from pedidos.models import Pedido

# Register your models here.

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # ... configuración existente ...
    
    def has_delete_permission(self, request, obj=None):
        # Solo administradores pueden eliminar
        return request.user.es_administrador
    
    def get_queryset(self, request):
        # Empleados ven todos los pedidos, clientes solo los suyos
        qs = super().get_queryset(request)
        if request.user.es_administrador or request.user.es_empleado:
            return qs
        return qs.filter(usuario=request.user)