from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from decimal import Decimal
from .models import Pedido, ItemPedido, SeguimientoPedido
from .forms import PedidoForm, ItemPedidoForm, DireccionEnvioForm, MetodoPagoForm, ConfirmacionPagoForm
from carrito.utils import obtener_carrito
from carrito.models import ItemCarrito
from confecciones.models import Confeccion

@login_required
def lista_pedidos(request):
    """Listar pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'pedidos/lista.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido específico"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'pedidos/detalle.html', {'pedido': pedido})

@login_required
def crear_pedido_desde_carrito(request):
    """Crear pedido desde el carrito de compras"""
    carrito = obtener_carrito(request)
    
    if not carrito or carrito.items.count() == 0:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito:detalle')
    
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear el pedido
                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        nombre_completo=form.cleaned_data['nombre_completo'],
                        email=form.cleaned_data['email'],
                        telefono=form.cleaned_data['telefono'],
                        direccion=form.cleaned_data['direccion'],
                        ciudad=form.cleaned_data['ciudad'],
                        codigo_postal=form.cleaned_data['codigo_postal'],
                        tipo_pedido='normal',
                        metodo_pago='efectivo',
                        estado='pendiente',
                        estado_pago='pendiente'
                    )
                    
                    # Mover items del carrito al pedido
                    for item_carrito in carrito.items.all():
                        ItemPedido.objects.create(
                            pedido=pedido,
                            producto=item_carrito.producto,
                            cantidad=item_carrito.cantidad,
                            precio_unitario=item_carrito.precio_unitario
                        )
                    
                    # Calcular totales
                    pedido.calcular_totales()
                    
                    # Limpiar carrito
                    carrito.items.all().delete()
                    
                    # Crear seguimiento inicial
                    SeguimientoPedido.objects.create(
                        pedido=pedido,
                        estado='pendiente',
                        observaciones='Pedido creado desde carrito',
                        usuario=request.user
                    )
                    
                    # Enviar email de confirmación
                    enviar_email_confirmacion(pedido)
                    
                    messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente!')
                    return redirect('pedidos:detalle', pedido_id=pedido.id)
                    
            except Exception as e:
                messages.error(request, f'Error al crear el pedido: {str(e)}')
                return redirect('carrito:detalle')
    else:
        # Prellenar formulario con datos del usuario
        initial_data = {
            'nombre_completo': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
            'telefono': request.user.telefono or '',
            'direccion': request.user.direccion or '',
            'ciudad': '',
            'codigo_postal': '',
        }
        form = DireccionEnvioForm(initial=initial_data)
    
    return render(request, 'pedidos/checkout.html', {
        'form': form,
        'carrito': carrito,
        'total': carrito.subtotal if carrito else 0
    })

@login_required
def crear_pedido_confeccion(request):
    """Crear pedido de confección personalizado"""
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            try:
                pedido = form.save(commit=False)
                pedido.usuario = request.user
                pedido.tipo_pedido = 'confeccion'
                pedido.estado = 'pendiente'
                pedido.estado_pago = 'pendiente'
                pedido.save()
                
                messages.success(request, f'¡Pedido de confección #{pedido.id} creado!')
                return redirect('confecciones:crear_detalle', pedido_id=pedido.id)
                
            except Exception as e:
                messages.error(request, f'Error al crear pedido: {str(e)}')
    else:
        # Prellenar con datos del usuario
        initial_data = {
            'nombre_completo': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
            'telefono': request.user.telefono or '',
            'direccion': request.user.direccion or '',
        }
        form = PedidoForm(initial=initial_data)
    
    return render(request, 'pedidos/crear_confeccion.html', {'form': form})

@login_required
def cancelar_pedido(request, pedido_id):
    """Cancelar un pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if not (request.user.es_administrador or (request.user == pedido.usuario and pedido.estado == 'pendiente')):
        pedido.estado = 'cancelado'
        pedido.save()
        
        SeguimientoPedido.objects.create(
            pedido=pedido,
            estado='cancelado',
            observaciones='Pedido cancelado',
            usuario=request.user
        )
        
        messages.success(request, f'Pedido #{pedido.id} cancelado exitosamente.')
    else:
        messages.error(request, 'No se puede cancelar el pedido en su estado actual.')
    
    return redirect('pedidos:lista')

# Vistas para empleados/administradores
@login_required
def gestion_pedidos(request):
    """Vista de gestión de pedidos para staff"""
    if not request.user.es_empleado and not request.user.es_administrador:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('productos:lista')
    
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    return render(request, 'pedidos/gestion.html', {'pedidos': pedidos})

@login_required
def cambiar_estado_pedido(request, pedido_id):
    """Cambiar estado de pedido (para staff)"""
    if not request.user.es_empleado and not request.user.es_administrador:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones', '')
        
        if nuevo_estado in dict(Pedido.ESTADOS_PEDIDO):
            pedido.estado = nuevo_estado
            pedido.save()
            
            SeguimientoPedido.objects.create(
                pedido=pedido,
                estado=nuevo_estado,
                observaciones=observaciones,
                usuario=request.user
            )
            
            return JsonResponse({'success': True, 'nuevo_estado': pedido.get_estado_display()})
    
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

# Vistas de Checkout
@login_required
def proceso_checkout(request):
    """Proceso completo de checkout en múltiples pasos"""
    carrito = obtener_carrito(request)
    
    if not carrito or carrito.items.count() == 0:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('carrito:detalle')
    
    # Obtener paso de GET parameter o default a 1
    paso = request.GET.get('paso', '1')
    
    if paso == '1':
        return paso_direccion(request, carrito)
    elif paso == '2':
        return paso_pago(request, carrito)
    elif paso == '3':
        return paso_confirmacion(request, carrito)
    else:
        # Si el paso no es válido, redirigir al paso 1
        return redirect('pedidos:checkout')
    
def paso_direccion(request, carrito):
    """Paso 1: Dirección de envío"""
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            request.session['datos_envio'] = form.cleaned_data
            # URL correcta con parámetro GET
            url = reverse('pedidos:checkout') + '?paso=2'
            return HttpResponseRedirect(url)
    else:
        # Prellenar con datos del usuario
        initial = {
            'nombre_completo': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
            'telefono': request.user.telefono or '',
            'direccion': request.user.direccion or '',
            'ciudad': '',
            'codigo_postal': '',
        }
        form = DireccionEnvioForm(initial=initial)
    
    return render(request, 'pedidos/checkout_paso1.html', {
        'form': form,
        'carrito': carrito,
        'paso': 1
    })

def paso_pago(request, carrito):
    """Paso 2: Método de pago"""
    if 'datos_envio' not in request.session:
        return redirect('pedidos:checkout')
    
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST)
        if form.is_valid():
            request.session['metodo_pago'] = form.cleaned_data['metodo_pago']
            # URL correcta con parámetro GET
            url = reverse('pedidos:checkout') + '?paso=3'
            return HttpResponseRedirect(url)
    else:
        form = MetodoPagoForm()
    
    return render(request, 'pedidos/checkout_paso2.html', {
        'form': form,
        'carrito': carrito,
        'paso': 2
    })
    
def paso_confirmacion(request, carrito):
    """Paso 3: Confirmación y pago"""
    if 'datos_envio' not in request.session or 'metodo_pago' not in request.session:
        return redirect('pedidos:checkout')
    
    metodo_pago = request.session['metodo_pago']
    
    if request.method == 'POST':
        if metodo_pago in ['tarjeta_credito', 'tarjeta_debito']:
            form = ConfirmacionPagoForm(request.POST)
            if not form.is_valid():
                return render(request, 'pedidos/checkout_paso3.html', {
                    'form': form,
                    'carrito': carrito,
                    'paso': 3,
                    'metodo_pago': metodo_pago
                })
        # Crear el pedido
        return crear_pedido_final(request, carrito)
    
    # Formulario para tarjetas, vacío para otros métodos
    form = ConfirmacionPagoForm() if metodo_pago in ['tarjeta_credito', 'tarjeta_debito'] else None
    
    return render(request, 'pedidos/checkout_paso3.html', {
        'form': form,
        'carrito': carrito,
        'paso': 3,
        'metodo_pago': metodo_pago,
        'datos_envio': request.session['datos_envio']
    })

@transaction.atomic
def crear_pedido_final(request, carrito):
    """Crear el pedido final con todos los datos"""
    try:
        datos_envio = request.session['datos_envio']
        metodo_pago = request.session['metodo_pago']
        
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            tipo_pedido='normal',
            estado='pendiente',
            estado_pago='pendiente',
            metodo_pago=metodo_pago,
            **datos_envio
        )
        
        # Mover items del carrito al pedido
        for item_carrito in carrito.items.all():
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_carrito.producto,
                cantidad=item_carrito.cantidad,
                precio_unitario=item_carrito.precio_unitario
            )
        
        # Calcular totales - Aquí puedes pasar un costo de envío personalizado si lo deseas
        # Por ejemplo, podrías tener un formulario donde el usuario elija el envío
        pedido.calcular_totales()  # O pedido.calcular_totales(Decimal('300')) para un costo fijo        
    except Exception as e:
        messages.error(request, f'Error al crear el pedido: {str(e)}')
        return redirect('carrito:detalle')

@login_required
def checkout_completado(request, pedido_id):
    """Página de pedido completado"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    return render(request, 'pedidos/completado.html', {'pedido': pedido})

def enviar_email_confirmacion(pedido):
    """Enviar email de confirmación de pedido"""
    try:
        subject = f'Confirmación de Pedido #{pedido.id}'
        message = f'''
        Hola {pedido.nombre_completo},
        
        Tu pedido #{pedido.id} ha sido creado exitosamente.
        
        Total: ${pedido.total}
        Estado: {pedido.get_estado_pago_display()}
        
        Gracias por tu compra!
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [pedido.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error enviando email: {e}")

@login_required
def modificar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if not pedido.puede_ser_modificado_por(request.user):
        messages.error(request, 'No tienes permisos para modificar este pedido.')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    # Lógica de modificación...

@login_required  
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if not pedido.puede_ser_eliminado_por(request.user):
        messages.error(request, 'No tienes permisos para eliminar este pedido.')
        return redirect('pedidos:detalle', pedido_id=pedido.id)
    
    # Lógica de eliminación...
