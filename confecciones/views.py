from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from pedidos.models import Pedido
from .models import Confeccion, DetalleConfeccion, ItemAdicional
from .forms import ConfeccionForm, DetalleConfeccionForm, ItemAdicionalForm, EstadoConfeccionForm

@login_required
def crear_detalle_confeccion(request, pedido_id):
    """Crear detalles de confección para un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    # Verificar que el pedido sea de confección
    if not pedido.es_pedido_confeccion:
        messages.error(request, 'Este pedido no es de confección.')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    # Obtener o crear la confección
    confeccion, created = Confeccion.objects.get_or_create(pedido=pedido)
    
    if request.method == 'POST':
        form = DetalleConfeccionForm(request.POST)
        if form.is_valid():
            try:
                detalle = form.save(commit=False)
                detalle.confeccion = confeccion
                detalle.save()
                
                messages.success(request, 'Detalle de confección agregado correctamente.')
                return redirect('confecciones:agregar_item_adicional', detalle_id=detalle.id)
                
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
    else:
        form = DetalleConfeccionForm()
    
    return render(request, 'confecciones/crear_detalle.html', {
        'form': form,
        'pedido': pedido,
        'confeccion': confeccion
    })

@login_required
def agregar_item_adicional(request, detalle_id):
    """Agregar items adicionales a un detalle de confección"""
    detalle = get_object_or_404(DetalleConfeccion, id=detalle_id)
    
    if request.method == 'POST':
        form = ItemAdicionalForm(request.POST)
        if form.is_valid():
            try:
                item = form.save(commit=False)
                item.detalle = detalle
                item.save()
                
                messages.success(request, 'Item adicional agregado correctamente.')
                return redirect('confecciones:agregar_item_adicional', detalle_id=detalle.id)
                
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
    else:
        form = ItemAdicionalForm()
    
    items_adicionales = detalle.items_adicionales.all()
    
    return render(request, 'confecciones/agregar_item.html', {
        'form': form,
        'detalle': detalle,
        'items_adicionales': items_adicionales
    })

@login_required
def finalizar_confeccion(request, confeccion_id):
    """Finalizar el proceso de configuración de confección"""
    confeccion = get_object_or_404(Confeccion, id=confeccion_id)
    
    # Calcular costo total estimado
    costo_total = 0
    for detalle in confeccion.detalles.all():
        costo_total += detalle.subtotal
        for item in detalle.items_adicionales.all():
            costo_total += item.subtotal
    
    confeccion.costo_estimado = costo_total
    confeccion.save()
    
    messages.success(request, f'Confección configurada correctamente. Costo estimado: ${costo_total:.2f}')
    return redirect('pedidos:detalle', pedido_id=confeccion.pedido.id)

@login_required
def detalle_confeccion(request, confeccion_id):
    """Ver detalle completo de una confección"""
    confeccion = get_object_or_404(Confeccion, id=confeccion_id)
    
    # Verificar permisos
    if not (request.user == confeccion.pedido.usuario or request.user.es_empleado or request.user.es_administrador):
        messages.error(request, 'No tienes permisos para ver esta confección.')
        return redirect('pedidos:lista')
    
    return render(request, 'confecciones/detalle.html', {'confeccion': confeccion})

# Vistas para empleados
@login_required
def gestion_confecciones(request):
    """Gestión de confecciones para empleados"""
    if not request.user.es_empleado and not request.user.es_administrador:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('productos:lista')
    
    confecciones = Confeccion.objects.all().order_by('prioridad', 'fecha_entrega')
    return render(request, 'confecciones/gestion.html', {'confecciones': confecciones})

@login_required
def cambiar_estado_confeccion(request, confeccion_id):
    """Cambiar estado de una confección"""
    if not request.user.es_empleado and not request.user.es_administrador:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('productos:lista')
    
    confeccion = get_object_or_404(Confeccion, id=confeccion_id)
    
    if request.method == 'POST':
        form = EstadoConfeccionForm(request.POST)
        if form.is_valid():
            confeccion.estado = form.cleaned_data['estado']
            
            # Si se marca como terminado, registrar fecha
            if confeccion.estado == 'terminado' and not confeccion.fecha_terminado:
                from django.utils import timezone
                confeccion.fecha_terminado = timezone.now()
            
            confeccion.save()
            
            messages.success(request, f'Estado actualizado a: {confeccion.get_estado_display()}')
        else:
            messages.error(request, 'Error al cambiar el estado.')
    
    return redirect('confecciones:gestion')

@login_required
def asignar_confeccion(request, confeccion_id):
    """Asignar confección a un empleado"""
    if not request.user.es_administrador:
        messages.error(request, 'Solo los administradores pueden asignar confecciones.')
        return redirect('confecciones:gestion')
    
    confeccion = get_object_or_404(Confeccion, id=confeccion_id)
    
    if request.method == 'POST':
        empleado_id = request.POST.get('empleado_id')
        from usuarios.models import Usuario
        try:
            empleado = Usuario.objects.get(id=empleado_id, rol='empleado')
            confeccion.asignado_a = empleado
            confeccion.save()
            messages.success(request, f'Confección asignada a {empleado.get_full_name()}')
        except Usuario.DoesNotExist:
            messages.error(request, 'Empleado no válido.')
    
    return redirect('confecciones:gestion')