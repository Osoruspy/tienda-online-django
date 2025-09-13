from django.contrib import admin
from .models import Confeccion, DetalleConfeccion, ItemAdicional

class ItemAdicionalInline(admin.TabularInline):
    model = ItemAdicional
    extra = 1

class DetalleConfeccionInline(admin.TabularInline):
    model = DetalleConfeccion
    extra = 1
    inlines = [ItemAdicionalInline]

@admin.register(Confeccion)
class ConfeccionAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'contacto', 'estado', 'prioridad', 'fecha_entrega', 'asignado_a']
    list_filter = ['estado', 'prioridad', 'fecha_creacion', 'asignado_a']
    search_fields = ['contacto', 'pedido__id', 'observaciones']
    readonly_fields = ['fecha_creacion']
    inlines = [DetalleConfeccionInline]
    fieldsets = (
        ('Información Principal', {
            'fields': ('pedido', 'estado', 'prioridad', 'asignado_a')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_entrega', 'fecha_terminado')
        }),
        ('Contacto', {
            'fields': ('contacto', 'telefono_contacto', 'email_contacto')
        }),
        ('Costos y Observaciones', {
            'fields': ('costo_estimado', 'observaciones')
        }),
    )

@admin.register(DetalleConfeccion)
class DetalleConfeccionAdmin(admin.ModelAdmin):
    list_display = ['confeccion', 'tipo_prenda', 'genero', 'talla', 'cantidad', 'precio_unitario']
    list_filter = ['tipo_prenda', 'genero', 'talla']

@admin.register(ItemAdicional)
class ItemAdicionalAdmin(admin.ModelAdmin):
    list_display = ['detalle', 'descripcion', 'cantidad', 'precio_adicional']