from django.contrib import admin
from .models import Categoria, Producto, ImagenProducto, Inventario

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

class InventarioInline(admin.StackedInline):
    model = Inventario
    can_delete = False

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'precio_oferta', 'stock', 'estado', 'destacado', 'disponible')
    list_filter = ('categoria', 'estado', 'destacado', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'sku')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenProductoInline, InventarioInline]
    
    def get_inlines(self, request, obj):
        if obj:
            return [ImagenProductoInline, InventarioInline]
        return [ImagenProductoInline]

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'orden', 'es_principal')
    list_editable = ('orden', 'es_principal')

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'stock_minimo', 'stock_maximo', 'necesita_reabastecimiento')
    search_fields = ('producto__nombre',)
