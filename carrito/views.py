from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Carrito, ItemCarrito
from .utils import obtener_carrito
from .forms import AgregarAlCarritoForm, ActualizarCantidadForm
from productos.models import Producto

def detalle_carrito(request):
    carrito = obtener_carrito(request)
    return render(request, 'carrito/detalle.html', {'carrito': carrito})

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, estado='activo')
    
    if not producto.disponible():
        messages.error(request, 'Este producto no está disponible.')
        return redirect('productos:lista')
    
    form = AgregarAlCarritoForm(request.POST or None)
    
    if form.is_valid():
        cantidad = form.cleaned_data['cantidad']
        
        if cantidad > producto.stock:
            messages.error(request, 'No hay suficiente stock disponible.')
            return redirect('productos:detalle', slug=producto.slug)
        
        carrito = obtener_carrito(request)
        
        # Verificar si el producto ya está en el carrito
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad, 'precio_unitario': producto.precio_actual()}
        )
        
        if not created:
            item.cantidad += cantidad
            item.save()
        
        messages.success(request, f'¡{producto.nombre} agregado al carrito!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Producto agregado al carrito',
                'total_items': carrito.total_items
            })
        
        return redirect('carrito:detalle')
    
    return redirect('productos:detalle', slug=producto.slug)

def actualizar_cantidad(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=obtener_carrito(request))
    
    if request.method == 'POST':
        form = ActualizarCantidadForm(request.POST, instance=item)
        if form.is_valid():
            if form.cleaned_data['cantidad'] > item.producto.stock:
                messages.error(request, 'No hay suficiente stock disponible.')
            else:
                form.save()
                messages.success(request, 'Cantidad actualizada.')
        else:
            messages.error(request, 'Error al actualizar la cantidad.')
    
    return redirect('carrito:detalle')

def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito=obtener_carrito(request))
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('carrito:detalle')

def vaciar_carrito(request):
    carrito = obtener_carrito(request)
    carrito.items.all().delete()
    messages.success(request, 'Carrito vaciado.')
    return redirect('carrito:detalle')

@login_required
def transferir_carrito_view(request):
    """Vista para transferir carrito de sesión a usuario"""
    from .utils import transferir_carrito_anonimo_a_usuario
    transferir_carrito_anonimo_a_usuario(request, request.user)
    messages.success(request, 'Carrito transferido a tu cuenta.')
    return redirect('carrito:detalle')
